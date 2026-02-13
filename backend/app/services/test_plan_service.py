"""Test plan service for business logic."""

from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.plan_scenario import PlanScenario
from app.models.scenario import Scenario
from app.models.test_plan import TestPlan
from app.schemas.test_plan import TestPlanCreate, TestPlanUpdate


class TestPlanService:
    """Service for test plan-related business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize test plan service.

        Args:
            db: Database session
        """
        self.db = db

    async def list_test_plans(
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        project_id: Optional[int] = None,
    ) -> tuple[List[TestPlan], int]:
        """List test plans with pagination and filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            name: Filter by plan name (partial match)
            project_id: Filter by project ID

        Returns:
            Tuple of (test plans list, total count)
        """
        # Build base query
        query = select(TestPlan)

        # Apply filters
        if name:
            query = query.where(TestPlan.name.ilike(f"%{name}%"))
        if project_id:
            query = query.where(TestPlan.project_id == project_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results with eager loading
        query = query.options(
            selectinload(TestPlan.creator),
            selectinload(TestPlan.project),
        )
        query = query.offset(skip).limit(limit)
        query = query.order_by(TestPlan.created_at.desc())

        result = await self.db.execute(query)
        test_plans = result.scalars().all()

        return list(test_plans), total

    async def get_test_plan_by_id(self, plan_id: int) -> Optional[TestPlan]:
        """Get test plan by ID with scenarios.

        Args:
            plan_id: Test plan ID

        Returns:
            TestPlan instance or None if not found
        """
        result = await self.db.execute(
            select(TestPlan)
            .options(
                selectinload(TestPlan.creator),
                selectinload(TestPlan.project),
            )
            .where(TestPlan.id == plan_id)
        )
        return result.scalar_one_or_none()

    async def get_test_plan_with_scenarios(self, plan_id: int) -> Optional[TestPlan]:
        """Get test plan by ID with scenarios.

        Args:
            plan_id: Test plan ID

        Returns:
            TestPlan instance with scenarios or None if not found
        """
        result = await self.db.execute(
            select(TestPlan)
            .options(
                selectinload(TestPlan.creator),
                selectinload(TestPlan.project),
            )
            .where(TestPlan.id == plan_id)
        )
        test_plan = result.scalar_one_or_none()

        if test_plan:
            # Load scenarios with sort_order
            scenarios_result = await self.db.execute(
                select(PlanScenario, Scenario)
                .join(Scenario, PlanScenario.scenario_id == Scenario.id)
                .where(PlanScenario.plan_id == plan_id)
                .order_by(PlanScenario.sort_order)
            )
            test_plan.scenarios_list = [
                ps[0] for ps in scenarios_result.all()
            ]

        return test_plan

    async def create_test_plan(
        self, plan_in: TestPlanCreate, creator_id: int
    ) -> TestPlan:
        """Create new test plan.

        Args:
            plan_in: Test plan creation data
            creator_id: ID of user creating the plan

        Returns:
            Created test plan instance

        Raises:
            ValueError: If test plan name already exists for this project
        """
        # Check if test plan name already exists for this project
        existing = await self.db.execute(
            select(TestPlan).where(
                TestPlan.project_id == plan_in.project_id,
                TestPlan.name == plan_in.name
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Test plan with this name already exists in this project")

        # Create test plan
        test_plan = TestPlan(
            name=plan_in.name,
            description=plan_in.description,
            project_id=plan_in.project_id,
            creator_id=creator_id,
        )
        self.db.add(test_plan)
        await self.db.flush()

        # Load relationships with eager loading
        result = await self.db.execute(
            select(TestPlan)
            .options(selectinload(TestPlan.creator), selectinload(TestPlan.project))
            .where(TestPlan.id == test_plan.id)
        )
        return result.scalar_one()

    async def update_test_plan(
        self, plan_id: int, plan_in: TestPlanUpdate
    ) -> Optional[TestPlan]:
        """Update test plan.

        Args:
            plan_id: Test plan ID
            plan_in: Test plan update data

        Returns:
            Updated test plan instance or None if not found

        Raises:
            ValueError: If test plan name already exists for this project
        """
        test_plan = await self.get_test_plan_by_id(plan_id)
        if not test_plan:
            return None

        # Check if new name conflicts with existing test plan
        if plan_in.name and plan_in.name != test_plan.name:
            existing = await self.db.execute(
                select(TestPlan).where(
                    TestPlan.project_id == test_plan.project_id,
                    TestPlan.name == plan_in.name,
                    TestPlan.id != plan_id,
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError("Test plan with this name already exists in this project")

        # Update fields
        update_data = plan_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(test_plan, field, value)

        await self.db.flush()
        await self.db.refresh(test_plan)
        return test_plan

    async def delete_test_plan(self, plan_id: int) -> bool:
        """Delete test plan.

        Args:
            plan_id: Test plan ID

        Returns:
            True if deleted, False if not found
        """
        test_plan = await self.get_test_plan_by_id(plan_id)
        if not test_plan:
            return False

        await self.db.delete(test_plan)
        await self.db.flush()
        return True

    async def add_scenario_to_plan(
        self, plan_id: int, scenario_id: int, sort_order: int
    ) -> PlanScenario:
        """Add scenario to test plan.

        Args:
            plan_id: Test plan ID
            scenario_id: Scenario ID
            sort_order: Execution order

        Returns:
            Created PlanScenario instance

        Raises:
            ValueError: If scenario already in plan
        """
        # Check if scenario already in plan
        existing = await self.db.execute(
            select(PlanScenario).where(
                PlanScenario.plan_id == plan_id,
                PlanScenario.scenario_id == scenario_id
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Scenario already added to this test plan")

        # Create plan-scenario association
        plan_scenario = PlanScenario(
            plan_id=plan_id,
            scenario_id=scenario_id,
            sort_order=sort_order,
        )
        self.db.add(plan_scenario)
        await self.db.flush()
        await self.db.refresh(plan_scenario)

        return plan_scenario

    async def reorder_scenarios(
        self, plan_id: int, scenario_orders: List[dict]
    ) -> List[PlanScenario]:
        """Reorder scenarios in test plan.

        Args:
            plan_id: Test plan ID
            scenario_orders: List of {'scenario_id': int, 'sort_order': int}

        Returns:
            Updated PlanScenario instances
        """
        plan_scenarios = []
        for item in scenario_orders:
            scenario_id = item.get("scenario_id")
            sort_order = item.get("sort_order")

            result = await self.db.execute(
                select(PlanScenario).where(
                    PlanScenario.plan_id == plan_id,
                    PlanScenario.scenario_id == scenario_id
                )
            )
            plan_scenario = result.scalar_one_or_none()

            if plan_scenario:
                plan_scenario.sort_order = sort_order
                plan_scenarios.append(plan_scenario)

        await self.db.flush()
        return plan_scenarios

    async def remove_scenario_from_plan(
        self, plan_id: int, scenario_id: int
    ) -> bool:
        """Remove scenario from test plan.

        Args:
            plan_id: Test plan ID
            scenario_id: Scenario ID

        Returns:
            True if removed, False if not found
        """
        result = await self.db.execute(
            select(PlanScenario).where(
                PlanScenario.plan_id == plan_id,
                PlanScenario.scenario_id == scenario_id
            )
        )
        plan_scenario = result.scalar_one_or_none()

        if not plan_scenario:
            return False

        await self.db.delete(plan_scenario)
        await self.db.flush()
        return True

    async def get_plan_scenarios(self, plan_id: int) -> List[dict]:
        """Get all scenarios in test plan.

        Args:
            plan_id: Test plan ID

        Returns:
            List of scenario info with sort_order
        """
        result = await self.db.execute(
            select(PlanScenario, Scenario)
            .join(Scenario, PlanScenario.scenario_id == Scenario.id)
            .where(PlanScenario.plan_id == plan_id)
            .order_by(PlanScenario.sort_order)
        )

        scenarios = []
        for ps, scenario in result.all():
            scenarios.append({
                "id": ps.id,
                "scenario_id": scenario.id,
                "scenario_name": scenario.name,
                "sort_order": ps.sort_order,
            })

        return scenarios
