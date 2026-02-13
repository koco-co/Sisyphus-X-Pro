"""Scenario API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.scenario import (
    CSVUploadResponse,
    DatasetResponse,
    ScenarioCreate,
    ScenarioListResponse,
    ScenarioResponse,
    ScenarioStepCreate,
    ScenarioStepResponse,
    ScenarioUpdate,
    StepReorderRequest,
)
from app.services.scenario_service import ScenarioService

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


def get_scenario_service(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> ScenarioService:
    """Get scenario service instance.

    Args:
        session: Database session

    Returns:
        ScenarioService instance
    """
    return ScenarioService(session)


@router.post("", response_model=ScenarioResponse, status_code=201)
async def create_scenario(
    scenario_data: ScenarioCreate,
    service: Annotated[ScenarioService, Depends(get_scenario_service)],
):
    """Create a new scenario.

    Args:
        scenario_data: Scenario creation data
        service: Scenario service

    Returns:
        Created scenario
    """
    scenario = await service.create_scenario(
        name=scenario_data.name,
        project_id=scenario_data.project_id,
        creator_id=1,  # TODO: Get from auth context
        description=scenario_data.description,
        priority=scenario_data.priority,
        tags=scenario_data.tags,
        pre_sql=scenario_data.pre_sql,
        post_sql=scenario_data.post_sql,
        variables=scenario_data.variables,
        environment_id=scenario_data.environment_id,
        steps_data=[step.model_dump() for step in scenario_data.steps],
    )

    # Load steps for response
    result = await service.get_scenario_by_id(scenario.id)
    return ScenarioResponse.model_validate(result)


@router.get("", response_model=list[ScenarioListResponse])
async def list_scenarios(
    service: Annotated[ScenarioService, Depends(get_scenario_service)],
    project_id: Annotated[int | None, Query(gt=0)] = None,
    limit: Annotated[int, Query(gt=0, le=100)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """List scenarios with optional filtering.

    Args:
        project_id: Optional project ID filter
        limit: Maximum number of results (default: 100)
        offset: Number of results to skip (default: 0)
        service: Scenario service

    Returns:
        List of scenarios
    """
    scenarios, _ = await service.list_scenarios(
        project_id=project_id,
        limit=limit,
        offset=offset,
    )

    return [ScenarioListResponse(**s) for s in scenarios]


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: int,
    service: Annotated[ScenarioService, Depends(get_scenario_service)],
):
    """Get scenario by ID.

    Args:
        scenario_id: Scenario ID
        service: Scenario service

    Returns:
        Scenario details

    Raises:
        HTTPException: If scenario not found
    """
    scenario = await service.get_scenario_by_id(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return ScenarioResponse.model_validate(scenario)


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: int,
    scenario_data: ScenarioUpdate,
    service: Annotated[ScenarioService, Depends(get_scenario_service)],
):
    """Update scenario.

    Args:
        scenario_id: Scenario ID
        scenario_data: Scenario update data
        service: Scenario service

    Returns:
        Updated scenario

    Raises:
        HTTPException: If scenario not found
    """
    scenario = await service.update_scenario(
        scenario_id=scenario_id,
        name=scenario_data.name,
        description=scenario_data.description,
        priority=scenario_data.priority,
        tags=scenario_data.tags,
        pre_sql=scenario_data.pre_sql,
        post_sql=scenario_data.post_sql,
        variables=scenario_data.variables,
        environment_id=scenario_data.environment_id,
    )

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return ScenarioResponse.model_validate(scenario)


@router.delete("/{scenario_id}")
async def delete_scenario(
    scenario_id: int,
    service: Annotated[ScenarioService, Depends(get_scenario_service)],
):
    """Delete scenario.

    Args:
        scenario_id: Scenario ID
        service: Scenario service

    Returns:
        Success message

    Raises:
        HTTPException: If scenario not found
    """
    success = await service.delete_scenario(scenario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return {"message": "Scenario deleted successfully"}


@router.post("/{scenario_id}/steps", response_model=ScenarioStepResponse, status_code=201)
async def add_step(
    scenario_id: int,
    step_data: ScenarioStepCreate,
    service: Annotated[ScenarioService, Depends(get_scenario_service)],
):
    """Add a step to scenario.

    Args:
        scenario_id: Scenario ID
        step_data: Step creation data
        service: Scenario service

    Returns:
        Created step

    Raises:
        HTTPException: If scenario not found
    """
    step = await service.add_step(
        scenario_id=scenario_id,
        description=step_data.description,
        keyword_id=step_data.keyword_id,
        params=step_data.params,
        sort_order=step_data.sort_order,
    )

    if not step:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return ScenarioStepResponse.model_validate(step)


@router.get("/{scenario_id}/steps", response_model=list[ScenarioStepResponse])
async def list_steps(
    scenario_id: int,
    service: Annotated[ScenarioService, Depends(get_scenario_service)],
):
    """List scenario steps.

    Args:
        scenario_id: Scenario ID
        service: Scenario service

    Returns:
        List of steps

    Raises:
        HTTPException: If scenario not found
    """
    scenario = await service.get_scenario_by_id(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Get steps ordered by sort_order
    from sqlalchemy import select

    from app.models.scenario_step import ScenarioStep

    result = await service.session.execute(
        select(ScenarioStep)
        .where(ScenarioStep.scenario_id == scenario_id)
        .order_by(ScenarioStep.sort_order)
    )
    steps = result.scalars().all()

    return [ScenarioStepResponse.model_validate(s) for s in steps]


@router.put("/{scenario_id}/steps/reorder")
async def reorder_steps(
    scenario_id: int,
    reorder_data: StepReorderRequest,
    service: Annotated[ScenarioService, Depends(get_scenario_service)],
):
    """Reorder scenario steps.

    Args:
        scenario_id: Scenario ID
        reorder_data: Step reordering data
        service: Scenario service

    Returns:
        Success message

    Raises:
        HTTPException: If scenario not found
    """
    success = await service.reorder_steps(scenario_id, reorder_data.step_ids)
    if not success:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return {"message": "Steps reordered successfully"}


@router.put("/{scenario_id}/pre-sql", response_model=ScenarioResponse)
async def update_pre_sql(
    scenario_id: int,
    sql_data: dict[str, str],
    service: Annotated[ScenarioService, Depends(get_scenario_service)],
):
    """Update scenario pre-SQL.

    Args:
        scenario_id: Scenario ID
        sql_data: SQL data with 'sql' key
        service: Scenario service

    Returns:
        Updated scenario

    Raises:
        HTTPException: If scenario not found
    """
    scenario = await service.update_scenario(
        scenario_id=scenario_id,
        pre_sql=sql_data.get("sql"),
    )

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return ScenarioResponse.model_validate(scenario)


@router.put("/{scenario_id}/post-sql", response_model=ScenarioResponse)
async def update_post_sql(
    scenario_id: int,
    sql_data: dict[str, str],
    service: Annotated[ScenarioService, Depends(get_scenario_service)],
):
    """Update scenario post-SQL.

    Args:
        scenario_id: Scenario ID
        sql_data: SQL data with 'sql' key
        service: Scenario service

    Returns:
        Updated scenario

    Raises:
        HTTPException: If scenario not found
    """
    scenario = await service.update_scenario(
        scenario_id=scenario_id,
        post_sql=sql_data.get("sql"),
    )

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return ScenarioResponse.model_validate(scenario)


@router.post("/{scenario_id}/dataset", response_model=CSVUploadResponse, status_code=201)
async def upload_dataset(
    scenario_id: int,
    file: Annotated[UploadFile, File(description="CSV file")],
    service: Annotated[ScenarioService, Depends(get_scenario_service)],
):
    """Upload CSV dataset for scenario.

    Args:
        scenario_id: Scenario ID
        file: Uploaded CSV file
        service: Scenario service

    Returns:
        Dataset upload response

    Raises:
        HTTPException: If scenario not found or file invalid
    """
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    csv_content = content.decode("utf-8")

    dataset = await service.create_dataset_from_csv(
        scenario_id=scenario_id,
        filename=file.filename or "uploaded.csv",
        csv_content=csv_content,
    )

    if not dataset:
        raise HTTPException(status_code=404, detail="Scenario not found")

    rows_count = len(dataset.rows)

    return CSVUploadResponse(
        dataset=DatasetResponse.model_validate(dataset),
        rows_count=rows_count,
    )


@router.get("/{scenario_id}/dataset", response_model=DatasetResponse)
async def get_dataset(
    scenario_id: int,
    service: Annotated[ScenarioService, Depends(get_scenario_service)],
):
    """Get scenario dataset.

    Args:
        scenario_id: Scenario ID
        service: Scenario service

    Returns:
        Dataset

    Raises:
        HTTPException: If dataset not found
    """
    dataset = await service.get_dataset_by_scenario(scenario_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return DatasetResponse.model_validate(dataset)
