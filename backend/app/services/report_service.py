"""Report service for business logic."""

import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.execution_scenario import ExecutionScenario
from app.models.execution_step import ExecutionStep
from app.models.test_execution import TestExecution
from app.models.test_report import TestReport


class ReportService:
    """Service for managing test reports."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize report service.

        Args:
            session: Database session
        """
        self.session = session

    async def create_report(
        self,
        execution_id: str,
        plan_id: int,
        executor_id: int,
        environment_name: str,
        started_at: datetime,
    ) -> TestReport:
        """Create a test report from execution data.

        Args:
            execution_id: Test execution ID
            plan_id: Test plan ID
            executor_id: Executor user ID
            environment_name: Environment name
            started_at: Execution start time

        Returns:
            Created test report
        """
        # Get execution data
        execution = await self.session.get(TestExecution, execution_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution {execution_id} not found",
            )

        # Calculate statistics
        total = execution.total_scenarios
        passed = execution.passed_scenarios
        failed = execution.failed_scenarios
        skipped = execution.skipped_scenarios

        # Calculate duration
        duration_seconds = None
        if execution.started_at and execution.finished_at:
            duration_seconds = (execution.finished_at - execution.started_at).total_seconds()

        # Create report
        report = TestReport(
            execution_id=execution_id,
            plan_id=plan_id,
            status=execution.status,
            total_scenarios=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration_seconds=duration_seconds,
            executor_id=executor_id,
            environment_name=environment_name,
            started_at=started_at,
            finished_at=execution.finished_at,
        )

        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)

        return report

    async def get_report_by_id(self, report_id: int) -> TestReport | None:
        """Get report by ID.

        Args:
            report_id: Report ID

        Returns:
            Test report or None
        """
        return await self.session.get(TestReport, report_id)

    async def get_reports(
        self,
        plan_id: int | None = None,
        status: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[TestReport], int]:
        """Get paginated list of reports.

        Args:
            plan_id: Filter by plan ID
            status: Filter by status
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (reports list, total count)
        """
        # Build query
        query = select(TestReport).order_by(TestReport.created_at.desc())

        # Apply filters
        conditions = []
        if plan_id is not None:
            conditions.append(TestReport.plan_id == plan_id)
        if status is not None:
            conditions.append(TestReport.status == status)

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(func.count()).select_from(TestReport)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        result = await self.session.execute(count_query)
        total = result.scalar_one()

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # Execute query
        result = await self.session.execute(query)
        reports = result.scalars().all()

        return list(reports), total

    async def delete_report(self, report_id: int) -> bool:
        """Delete a report.

        Args:
            report_id: Report ID

        Returns:
            True if deleted
        """
        report = await self.session.get(TestReport, report_id)
        if not report:
            return False

        # Delete Allure report files
        if report.allure_path:
            try:
                allure_dir = Path(report.allure_path)
                if allure_dir.exists():
                    shutil.rmtree(allure_dir)
            except Exception as e:
                # Log error but don't fail deletion
                print(f"Error deleting allure report: {e}")

        await self.session.delete(report)
        await self.session.commit()

        return True

    async def cleanup_old_reports(self, days: int = 30) -> int:
        """Delete reports older than specified days.

        Args:
            days: Number of days to retain reports

        Returns:
            Number of deleted reports
        """
        cutoff = datetime.now() - timedelta(days=days)

        # Find old reports
        query = select(TestReport).where(TestReport.created_at < cutoff)
        result = await self.session.execute(query)
        old_reports = result.scalars().all()

        # Delete reports and their Allure files
        deleted_count = 0
        for report in old_reports:
            # Delete Allure files
            if report.allure_path:
                try:
                    allure_dir = Path(report.allure_path)
                    if allure_dir.exists():
                        shutil.rmtree(allure_dir)
                except Exception as e:
                    print(f"Error deleting allure report: {e}")

            # Delete database record
            await self.session.delete(report)
            deleted_count += 1

        await self.session.commit()
        return deleted_count

    async def get_allure_report_url(self, report_id: int) -> tuple[str, datetime | None]:
        """Get Allure report URL for a report.

        Args:
            report_id: Report ID

        Returns:
            Tuple of (URL, expiration time)
        """
        report = await self.get_report_by_id(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found",
            )

        if not report.allure_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Allure report not available",
            )

        # Check if report exists
        allure_dir = Path(report.allure_path)
        if not allure_dir.exists():
            # Generate Allure report
            await self._generate_allure_report(report)

        # Return URL
        url = f"/allure/{report.execution_id}/index.html"
        return url, report.allure_expires_at

    async def _generate_allure_report(self, report: TestReport) -> None:
        """Generate Allure report from execution data.

        Args:
            report: Test report
        """
        # Create output directory
        output_dir = Path(f"/tmp/allure-reports/{report.execution_id}")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Assume allure results are in /tmp/allure-results/{execution_id}
        results_dir = Path(f"/tmp/allure-results/{report.execution_id}")

        if results_dir.exists():
            # Generate Allure report
            try:
                subprocess.run(
                    [
                        "allure",
                        "generate",
                        str(results_dir),
                        "-o",
                        str(output_dir),
                        "--clean",
                    ],
                    check=True,
                    capture_output=True,
                )

                # Update report with Allure path
                report.allure_path = str(output_dir)
                report.allure_expires_at = datetime.now() + timedelta(days=7)
                await self.session.commit()
            except subprocess.CalledProcessError as e:
                print(f"Error generating Allure report: {e}")
                raise

    async def get_report_statistics(self) -> dict:
        """Get report statistics.

        Returns:
            Dictionary with statistics
        """
        # Get total reports
        total_reports_result = await self.session.execute(
            select(func.count()).select_from(TestReport)
        )
        total_reports = total_reports_result.scalar_one()

        # Get sums
        stats_result = await self.session.execute(
            select(
                func.sum(TestReport.total_scenarios).label("total_scenarios"),
                func.sum(TestReport.passed).label("total_passed"),
                func.sum(TestReport.failed).label("total_failed"),
                func.sum(TestReport.skipped).label("total_skipped"),
                func.avg(TestReport.duration_seconds).label("avg_duration"),
            )
        )
        stats = stats_result.one()

        total_scenarios = stats.total_scenarios or 0
        total_passed = stats.total_passed or 0
        total_failed = stats.total_failed or 0
        total_skipped = stats.total_skipped or 0
        avg_duration = stats.avg_duration

        # Calculate pass rate
        pass_rate = 0.0
        if total_scenarios > 0:
            pass_rate = (total_passed / total_scenarios) * 100

        return {
            "total_reports": total_reports,
            "total_scenarios": total_scenarios,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_skipped": total_skipped,
            "pass_rate": pass_rate,
            "average_duration": avg_duration,
        }

    async def get_report_details(self, report_id: int) -> dict:
        """Get detailed report information including execution steps.

        Args:
            report_id: Report ID

        Returns:
            Dictionary with report details
        """
        report = await self.get_report_by_id(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found",
            )

        # Get execution scenarios
        scenarios_query = select(ExecutionScenario).where(
            ExecutionScenario.execution_id == report.execution_id
        )
        scenarios_result = await self.session.execute(scenarios_query)
        scenarios = scenarios_result.scalars().all()

        # Get execution steps for each scenario
        scenario_details = []
        for scenario in scenarios:
            steps_query = select(ExecutionStep).where(
                ExecutionStep.execution_scenario_id == scenario.id
            )
            steps_result = await self.session.execute(steps_query)
            steps = steps_result.scalars().all()

            scenario_details.append(
                {
                    "scenario_id": scenario.scenario_id,
                    "status": scenario.status,
                    "elapsed_ms": scenario.elapsed_ms,
                    "error_message": scenario.error_message,
                    "steps": [
                        {
                            "step_id": step.step_id,
                            "sort_order": step.sort_order,
                            "status": step.status,
                            "elapsed_ms": step.elapsed_ms,
                            "error_message": step.error_message,
                        }
                        for step in steps
                    ],
                }
            )

        return {
            "report": report,
            "scenarios": scenario_details,
        }
