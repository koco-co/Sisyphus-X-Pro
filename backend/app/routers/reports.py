"""Reports router for test report endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.report import (
    AllureReportResponse,
    ReportExportRequest,
    ReportListResponse,
    ReportResponse,
    ReportStatistics,
)
from app.services.report_export_service import ReportExportService
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=ReportListResponse)
async def get_reports(
    plan_id: int | None = Query(None, description="Filter by plan ID"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_db),
) -> ReportListResponse:
    """Get paginated list of test reports.

    Args:
        plan_id: Filter by plan ID
        status_filter: Filter by status
        page: Page number (1-indexed)
        limit: Items per page
        session: Database session

    Returns:
        Paginated list of reports
    """
    service = ReportService(session)
    reports, total = await service.get_reports(
        plan_id=plan_id,
        status=status_filter,
        page=page,
        limit=limit,
    )

    return ReportListResponse(
        reports=[ReportResponse.model_validate(report) for report in reports],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/statistics", response_model=ReportStatistics)
async def get_report_statistics(
    session: AsyncSession = Depends(get_db),
) -> ReportStatistics:
    """Get report statistics.

    Args:
        session: Database session

    Returns:
        Report statistics
    """
    service = ReportService(session)
    stats = await service.get_report_statistics()

    return ReportStatistics(**stats)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    session: AsyncSession = Depends(get_db),
) -> ReportResponse:
    """Get report by ID.

    Args:
        report_id: Report ID
        session: Database session

    Returns:
        Report details

    Raises:
        HTTPException: If report not found
    """
    service = ReportService(session)
    report = await service.get_report_by_id(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found",
        )

    return ReportResponse.model_validate(report)


@router.get("/{report_id}/allure", response_model=AllureReportResponse)
async def get_allure_report(
    report_id: int,
    session: AsyncSession = Depends(get_db),
) -> AllureReportResponse:
    """Get Allure report URL for a report.

    Args:
        report_id: Report ID
        session: Database session

    Returns:
        Allure report URL

    Raises:
        HTTPException: If report not found or Allure not available
    """
    service = ReportService(session)
    url, expires_at = await service.get_allure_report_url(report_id)

    return AllureReportResponse(url=url, expires_at=expires_at)


@router.post("/{report_id}/export")
async def export_report(
    report_id: int,
    export_request: ReportExportRequest,
    session: AsyncSession = Depends(get_db),
) -> Response:
    """Export report in specified format.

    Args:
        report_id: Report ID
        export_request: Export configuration
        session: Database session

    Returns:
        Exported file

    Raises:
        HTTPException: If export fails
    """
    export_service = ReportExportService(session)

    # Export based on format
    format_type = export_request.format.lower()

    if format_type == "pdf":
        content = await export_service.export_pdf(
            report_id,
            include_details=export_request.include_details,
        )
        media_type = "application/pdf"
        filename = f"report_{report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    elif format_type == "excel":
        content = await export_service.export_excel(
            report_id,
            include_details=export_request.include_details,
        )
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"report_{report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    elif format_type == "html":
        content = await export_service.export_html(
            report_id,
            include_details=export_request.include_details,
        )
        media_type = "text/html"
        filename = f"report_{report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format_type}. Supported: pdf, excel, html",
        )

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete a report.

    Args:
        report_id: Report ID
        session: Database session

    Raises:
        HTTPException: If report not found
    """
    service = ReportService(session)
    deleted = await service.delete_report(report_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found",
        )
