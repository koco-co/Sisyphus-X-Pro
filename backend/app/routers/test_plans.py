"""Test plan router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.test_plan import (
    ScenarioInPlan,
    TestPlanCreate,
    TestPlanDetailResponse,
    TestPlanListResponse,
    TestPlanResponse,
    TestPlanUpdate,
)
from app.services.test_plan_service import TestPlanService

router = APIRouter(prefix="/test-plans", tags=["Test Plans"])


async def get_test_plan_service(
    db: AsyncSession = Depends(get_db),
) -> TestPlanService:
    """Dependency to get test plan service.

    Args:
        db: Database session

    Returns:
        TestPlanService instance
    """
    return TestPlanService(db)


@router.get("", response_model=TestPlanListResponse)
async def list_test_plans(
    page: Annotated[int, Query(ge=1, description="页码")] = 1,
    pageSize: Annotated[int, Query(ge=1, le=100, description="每页条数")] = 10,  # noqa: N803
    name: Annotated[str | None, Query(description="计划名称(模糊搜索)")] = None,
    project_id: Annotated[int | None, Query(description="项目 ID")] = None,
    current_user: User = Depends(get_current_user),
    test_plan_service: TestPlanService = Depends(get_test_plan_service),
):
    """List test plans with pagination and search.

    Args:
        page: Page number (1-indexed)
        pageSize: Number of items per page
        name: Filter by plan name (partial match)
        project_id: Filter by project ID
        current_user: Current authenticated user
        test_plan_service: Test plan service

    Returns:
        Paginated list of test plans
    """
    skip = (page - 1) * pageSize
    test_plans, total = await test_plan_service.list_test_plans(
        skip=skip, limit=pageSize, name=name, project_id=project_id
    )

    # Convert to response models
    items = [
        TestPlanResponse(
            id=tp.id,
            name=tp.name,
            description=tp.description,
            project_id=tp.project_id,
            project_name=tp.project.name,
            creator_name=tp.creator.nickname,
            created_at=tp.created_at,
            updated_at=tp.updated_at,
        )
        for tp in test_plans
    ]

    return TestPlanListResponse(items=items, total=total, page=page, pageSize=pageSize)


@router.post("", response_model=TestPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_test_plan(
    plan_in: TestPlanCreate,
    current_user: User = Depends(get_current_user),
    test_plan_service: TestPlanService = Depends(get_test_plan_service),
):
    """Create new test plan.

    Args:
        plan_in: Test plan creation data
        current_user: Current authenticated user
        test_plan_service: Test plan service

    Returns:
        Created test plan

    Raises:
        HTTPException: If plan name already exists
    """
    try:
        test_plan = await test_plan_service.create_test_plan(plan_in, current_user.id)
        return TestPlanResponse(
            id=test_plan.id,
            name=test_plan.name,
            description=test_plan.description,
            project_id=test_plan.project_id,
            project_name=test_plan.project.name,
            creator_name=test_plan.creator.nickname,
            created_at=test_plan.created_at,
            updated_at=test_plan.updated_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{plan_id}", response_model=TestPlanDetailResponse)
async def get_test_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    test_plan_service: TestPlanService = Depends(get_test_plan_service),
):
    """Get test plan by ID with scenarios.

    Args:
        plan_id: Test plan ID
        current_user: Current authenticated user
        test_plan_service: Test plan service

    Returns:
        Test plan details with scenarios

    Raises:
        HTTPException: If test plan not found
    """
    test_plan = await test_plan_service.get_test_plan_with_scenarios(plan_id)
    if not test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test plan not found",
        )

    # Get scenarios list
    scenarios = await test_plan_service.get_plan_scenarios(plan_id)
    scenario_responses = [
        ScenarioInPlan(**s) for s in scenarios
    ]

    return TestPlanDetailResponse(
        id=test_plan.id,
        name=test_plan.name,
        description=test_plan.description,
        project_id=test_plan.project_id,
        project_name=test_plan.project.name,
        creator_name=test_plan.creator.nickname,
        created_at=test_plan.created_at,
        updated_at=test_plan.updated_at,
        scenarios=scenario_responses,
    )


@router.put("/{plan_id}", response_model=TestPlanResponse)
async def update_test_plan(
    plan_id: int,
    plan_in: TestPlanUpdate,
    current_user: User = Depends(get_current_user),
    test_plan_service: TestPlanService = Depends(get_test_plan_service),
):
    """Update test plan.

    Args:
        plan_id: Test plan ID
        plan_in: Test plan update data
        current_user: Current authenticated user
        test_plan_service: Test plan service

    Returns:
        Updated test plan

    Raises:
        HTTPException: If test plan not found or name conflict
    """
    try:
        test_plan = await test_plan_service.update_test_plan(plan_id, plan_in)
        if not test_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test plan not found",
            )

        return TestPlanResponse(
            id=test_plan.id,
            name=test_plan.name,
            description=test_plan.description,
            project_id=test_plan.project_id,
            project_name=test_plan.project.name,
            creator_name=test_plan.creator.nickname,
            created_at=test_plan.created_at,
            updated_at=test_plan.updated_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    test_plan_service: TestPlanService = Depends(get_test_plan_service),
):
    """Delete test plan.

    Args:
        plan_id: Test plan ID
        current_user: Current authenticated user
        test_plan_service: Test plan service

    Raises:
        HTTPException: If test plan not found
    """
    deleted = await test_plan_service.delete_test_plan(plan_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test plan not found",
        )


@router.post("/{plan_id}/scenarios", status_code=status.HTTP_201_CREATED)
async def add_scenario_to_plan(
    plan_id: int,
    scenario_id: int,
    sort_order: Annotated[int, Query(ge=0, description="执行顺序")] = 0,
    current_user: User = Depends(get_current_user),
    test_plan_service: TestPlanService = Depends(get_test_plan_service),
):
    """Add scenario to test plan.

    Args:
        plan_id: Test plan ID
        scenario_id: Scenario ID
        sort_order: Execution order
        current_user: Current authenticated user
        test_plan_service: Test plan service

    Returns:
        Created plan-scenario association

    Raises:
        HTTPException: If test plan not found or scenario already added
    """
    # Verify test plan exists
    test_plan = await test_plan_service.get_test_plan_by_id(plan_id)
    if not test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test plan not found",
        )

    try:
        plan_scenario = await test_plan_service.add_scenario_to_plan(
            plan_id, scenario_id, sort_order
        )
        return {
            "id": plan_scenario.id,
            "scenario_id": plan_scenario.scenario_id,
            "sort_order": plan_scenario.sort_order,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put("/{plan_id}/scenarios/reorder")
async def reorder_scenarios(
    plan_id: int,
    scenario_orders: list[dict],
    current_user: User = Depends(get_current_user),
    test_plan_service: TestPlanService = Depends(get_test_plan_service),
):
    """Reorder scenarios in test plan.

    Args:
        plan_id: Test plan ID
        scenario_orders: List of {'scenario_id': int, 'sort_order': int}
        current_user: Current authenticated user
        test_plan_service: Test plan service

    Returns:
        Updated plan-scenario associations

    Raises:
        HTTPException: If test plan not found
    """
    # Verify test plan exists
    test_plan = await test_plan_service.get_test_plan_by_id(plan_id)
    if not test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test plan not found",
        )

    await test_plan_service.reorder_scenarios(plan_id, scenario_orders)
    return {"message": "Scenarios reordered successfully"}


@router.delete("/{plan_id}/scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_scenario_from_plan(
    plan_id: int,
    scenario_id: int,
    current_user: User = Depends(get_current_user),
    test_plan_service: TestPlanService = Depends(get_test_plan_service),
):
    """Remove scenario from test plan.

    Args:
        plan_id: Test plan ID
        scenario_id: Scenario ID
        current_user: Current authenticated user
        test_plan_service: Test plan service

    Raises:
        HTTPException: If test plan not found or scenario not in plan
    """
    # Verify test plan exists
    test_plan = await test_plan_service.get_test_plan_by_id(plan_id)
    if not test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test plan not found",
        )

    removed = await test_plan_service.remove_scenario_from_plan(plan_id, scenario_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found in this test plan",
        )
