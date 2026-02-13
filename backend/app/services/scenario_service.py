"""Scenario service layer for business logic."""

import csv
from io import StringIO

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset
from app.models.scenario import Scenario
from app.models.scenario_step import ScenarioStep


class ScenarioService:
    """Service for scenario business logic."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize scenario service.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create_scenario(
        self,
        name: str,
        project_id: int,
        creator_id: int,
        description: str | None = None,
        priority: str = "P2",
        tags: dict | None = None,
        pre_sql: str | None = None,
        post_sql: str | None = None,
        variables: dict | None = None,
        environment_id: int | None = None,
        steps_data: list[dict] | None = None,
    ) -> Scenario:
        """Create a new scenario with optional steps.

        Args:
            name: Scenario name
            project_id: Project ID
            creator_id: Creator user ID
            description: Optional description
            priority: Priority level (P0/P1/P2/P3)
            tags: Optional tags dictionary
            pre_sql: Optional pre-execution SQL
            post_sql: Optional post-execution SQL
            variables: Optional variables dictionary
            environment_id: Optional environment ID
            steps_data: Optional list of step data

        Returns:
            Created scenario
        """
        scenario = Scenario(
            name=name,
            project_id=project_id,
            creator_id=creator_id,
            description=description,
            priority=priority,
            tags=tags or {},
            pre_sql=pre_sql,
            post_sql=post_sql,
            variables=variables or {},
            environment_id=environment_id,
        )

        self.session.add(scenario)
        await self.session.flush()

        # Create steps if provided
        if steps_data:
            for step_data in steps_data:
                step = ScenarioStep(
                    scenario_id=scenario.id,
                    description=step_data["description"],
                    keyword_id=step_data["keyword_id"],
                    params=step_data.get("params", {}),
                    sort_order=step_data.get("sort_order", 0),
                )
                self.session.add(step)

        await self.session.commit()
        await self.session.refresh(scenario)

        return scenario

    async def get_scenario_by_id(self, scenario_id: int) -> Scenario | None:
        """Get scenario by ID with steps.

        Args:
            scenario_id: Scenario ID

        Returns:
            Scenario if found, None otherwise
        """
        from sqlalchemy.orm import selectinload

        result = await self.session.execute(
            select(Scenario)
            .options(selectinload(Scenario.steps))
            .where(Scenario.id == scenario_id)
        )
        return result.scalar_one_or_none()

    async def list_scenarios(
        self,
        project_id: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        """List scenarios with optional filtering.

        Args:
            project_id: Optional project ID filter
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (scenarios list, total count)
        """
        # Build query
        query = select(Scenario)
        count_query = select(func.count()).select_from(Scenario)

        if project_id:
            query = query.where(Scenario.project_id == project_id)
            count_query = count_query.where(Scenario.project_id == project_id)

        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Get scenarios with step count
        query = (
            query.add_columns(func.count(ScenarioStep.id).label("step_count"))
            .outerjoin(ScenarioStep, Scenario.id == ScenarioStep.scenario_id)
            .group_by(Scenario.id)
            .order_by(Scenario.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        rows = result.all()

        scenarios = []
        for row in rows:
            scenario = row[0]
            step_count = row[1] or 0
            scenarios.append(
                {
                    "id": scenario.id,
                    "name": scenario.name,
                    "description": scenario.description,
                    "priority": scenario.priority,
                    "tags": scenario.tags,
                    "created_at": scenario.created_at,
                    "updated_at": scenario.updated_at,
                    "step_count": step_count,
                }
            )

        return scenarios, total

    async def update_scenario(
        self,
        scenario_id: int,
        name: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        tags: dict | None = None,
        pre_sql: str | None = None,
        post_sql: str | None = None,
        variables: dict | None = None,
        environment_id: int | None = None,
    ) -> Scenario | None:
        """Update scenario.

        Args:
            scenario_id: Scenario ID
            name: Optional new name
            description: Optional new description
            priority: Optional new priority
            tags: Optional new tags
            pre_sql: Optional new pre-SQL
            post_sql: Optional new post-SQL
            variables: Optional new variables
            environment_id: Optional new environment ID

        Returns:
            Updated scenario if found, None otherwise
        """
        scenario = await self.get_scenario_by_id(scenario_id)
        if not scenario:
            return None

        if name is not None:
            scenario.name = name
        if description is not None:
            scenario.description = description
        if priority is not None:
            scenario.priority = priority
        if tags is not None:
            scenario.tags = tags
        if pre_sql is not None:
            scenario.pre_sql = pre_sql
        if post_sql is not None:
            scenario.post_sql = post_sql
        if variables is not None:
            scenario.variables = variables
        if environment_id is not None:
            scenario.environment_id = environment_id

        await self.session.commit()
        await self.session.refresh(scenario)

        return scenario

    async def delete_scenario(self, scenario_id: int) -> bool:
        """Delete scenario.

        Args:
            scenario_id: Scenario ID

        Returns:
            True if deleted, False if not found
        """
        scenario = await self.get_scenario_by_id(scenario_id)
        if not scenario:
            return False

        await self.session.delete(scenario)
        await self.session.commit()

        return True

    async def add_step(
        self,
        scenario_id: int,
        description: str,
        keyword_id: int,
        params: dict,
        sort_order: int = 0,
    ) -> ScenarioStep | None:
        """Add a step to scenario.

        Args:
            scenario_id: Scenario ID
            description: Step description
            keyword_id: Keyword ID
            params: Keyword parameters
            sort_order: Sort order

        Returns:
            Created step if scenario exists, None otherwise
        """
        scenario = await self.get_scenario_by_id(scenario_id)
        if not scenario:
            return None

        step = ScenarioStep(
            scenario_id=scenario_id,
            description=description,
            keyword_id=keyword_id,
            params=params,
            sort_order=sort_order,
        )

        self.session.add(step)
        await self.session.commit()
        await self.session.refresh(step)

        return step

    async def reorder_steps(self, scenario_id: int, step_ids: list[int]) -> bool:
        """Reorder scenario steps.

        Args:
            scenario_id: Scenario ID
            step_ids: List of step IDs in new order

        Returns:
            True if successful, False if scenario not found
        """
        scenario = await self.get_scenario_by_id(scenario_id)
        if not scenario:
            return False

        # Update sort_order for each step
        for idx, step_id in enumerate(step_ids):
            step = await self.session.get(ScenarioStep, step_id)
            if step and step.scenario_id == scenario_id:
                step.sort_order = idx

        await self.session.commit()
        return True

    async def update_step(
        self,
        step_id: int,
        description: str | None = None,
        keyword_id: int | None = None,
        params: dict | None = None,
        sort_order: int | None = None,
    ) -> ScenarioStep | None:
        """Update a scenario step.

        Args:
            step_id: Step ID
            description: Optional new description
            keyword_id: Optional new keyword ID
            params: Optional new parameters
            sort_order: Optional new sort order

        Returns:
            Updated step if found, None otherwise
        """
        step = await self.session.get(ScenarioStep, step_id)
        if not step:
            return None

        if description is not None:
            step.description = description
        if keyword_id is not None:
            step.keyword_id = keyword_id
        if params is not None:
            step.params = params
        if sort_order is not None:
            step.sort_order = sort_order

        await self.session.commit()
        await self.session.refresh(step)

        return step

    async def delete_step(self, step_id: int) -> bool:
        """Delete a scenario step.

        Args:
            step_id: Step ID

        Returns:
            True if deleted, False if not found
        """
        step = await self.session.get(ScenarioStep, step_id)
        if not step:
            return False

        await self.session.delete(step)
        await self.session.commit()

        return True

    async def create_dataset_from_csv(
        self,
        scenario_id: int,
        filename: str,
        csv_content: str,
    ) -> Dataset | None:
        """Create dataset from CSV content.

        Args:
            scenario_id: Scenario ID
            filename: CSV filename
            csv_content: CSV file content

        Returns:
            Created dataset if scenario exists, None otherwise
        """
        scenario = await self.get_scenario_by_id(scenario_id)
        if not scenario:
            return None

        # Parse CSV
        csv_reader = csv.reader(StringIO(csv_content))
        rows = list(csv_reader)

        if not rows:
            return None

        headers = rows[0]
        data_rows = rows[1:]

        dataset = Dataset(
            scenario_id=scenario_id,
            name=filename,
            headers=headers,
            rows=data_rows,
        )

        self.session.add(dataset)
        await self.session.commit()
        await self.session.refresh(dataset)

        return dataset

    async def get_dataset_by_scenario(self, scenario_id: int) -> Dataset | None:
        """Get dataset for scenario.

        Args:
            scenario_id: Scenario ID

        Returns:
            Dataset if found, None otherwise
        """
        result = await self.session.execute(
            select(Dataset).where(Dataset.scenario_id == scenario_id)
        )
        return result.scalar_one_or_none()
