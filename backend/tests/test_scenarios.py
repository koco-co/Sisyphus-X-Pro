"""Unit tests for scenario API endpoints."""

from datetime import datetime

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.keyword import Keyword


@pytest_asyncio.fixture(scope="function")
async def test_keywords(async_session: AsyncSession) -> list[Keyword]:
    """Create test keywords."""
    keywords = [
        Keyword(
            type="http_request",
            name="发送GET请求",
            method_name="send_get_request",
            code="def send_get_request(url, headers=None): ...",
            params=[
                {"name": "url", "description": "请求URL", "type": "string", "required": True},
                {"name": "headers", "description": "请求头", "type": "dict", "required": False},
            ],
            is_builtin=True,
            is_enabled=True,
        ),
        Keyword(
            type="assertion",
            name="断言状态码",
            method_name="assert_status_code",
            code="def assert_status_code(response, expected): ...",
            params=[
                {"name": "response", "description": "响应对象", "type": "object", "required": True},
                {"name": "expected", "description": "期望状态码", "type": "int", "required": True},
            ],
            is_builtin=True,
            is_enabled=True,
        ),
        Keyword(
            type="extract",
            name="提取JSON字段",
            method_name="extract_json_field",
            code="def extract_json_field(response, field_path): ...",
            params=[
                {"name": "response", "description": "响应对象", "type": "object", "required": True},
                {"name": "field_path", "description": "字段路径", "type": "string", "required": True},
            ],
            is_builtin=True,
            is_enabled=True,
        ),
    ]
    for keyword in keywords:
        async_session.add(keyword)
    await async_session.commit()
    for keyword in keywords:
        await async_session.refresh(keyword)
    return keywords


class TestScenarioCreation:
    """Test scenario creation endpoints."""

    @pytest.mark.asyncio
    async def test_create_scenario_success(
        self, client: AsyncClient, test_project, test_user
    ):
        """Test successful scenario creation."""
        response = await client.post(
            "/api/v1/scenarios",
            json={
                "name": "Login Scenario",
                "description": "Test user login flow",
                "priority": "P1",
                "project_id": test_project.id,
                "creator_id": test_user.id,
                "tags": {"auth": "login"},
            },
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["name"] == "Login Scenario"
        assert data["description"] == "Test user login flow"
        assert data["priority"] == "P1"
        assert data["project_id"] == test_project.id
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_scenario_with_steps(
        self, client: AsyncClient, test_project, test_user, test_keywords: list[Keyword]
    ):
        """Test creating scenario with steps."""
        response = await client.post(
            "/api/v1/scenarios",
            json={
                "name": "API Test Scenario",
                "project_id": test_project.id,
                "creator_id": test_user.id,
                "steps": [
                    {
                        "description": "Send GET request",
                        "keyword_id": test_keywords[0].id,
                        "params": {"url": "https://api.example.com/users"},
                        "sort_order": 0,
                    },
                    {
                        "description": "Assert status code",
                        "keyword_id": test_keywords[1].id,
                        "params": {"expected": 200},
                        "sort_order": 1,
                    },
                ],
            },
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert len(data["steps"]) == 2
        assert data["steps"][0]["sort_order"] == 0
        assert data["steps"][1]["sort_order"] == 1

    @pytest.mark.asyncio
    async def test_create_scenario_invalid_priority(self, client: AsyncClient, test_project, test_user):
        """Test scenario creation with invalid priority."""
        response = await client.post(
            "/api/v1/scenarios",
            json={
                "name": "Invalid Scenario",
                "project_id": test_project.id,
                "creator_id": test_user.id,
                "priority": "P5",  # Invalid priority
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_scenario_missing_name(self, client: AsyncClient, test_project, test_user):
        """Test scenario creation without name."""
        response = await client.post(
            "/api/v1/scenarios",
            json={
                "project_id": test_project.id,
                "creator_id": test_user.id,
            },
        )
        assert response.status_code == 422


class TestScenarioList:
    """Test scenario listing endpoints."""

    @pytest.mark.asyncio
    async def test_list_scenarios_by_project(
        self, client: AsyncClient, test_project, test_user
    ):
        """Test listing scenarios by project."""
        # Create multiple scenarios
        for i in range(3):
            await client.post(
                "/api/v1/scenarios",
                json={
                    "name": f"Scenario {i}",
                    "project_id": test_project.id,
                    "creator_id": test_user.id,
                },
            )

        response = await client.get(f"/api/v1/scenarios?project_id={test_project.id}")
        assert response.status_code in (200, 201)
        data = response.json()
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_list_scenarios_empty(self, client: AsyncClient, test_project):
        """Test listing scenarios when none exist."""
        response = await client.get(f"/api/v1/scenarios?project_id={test_project.id}")
        assert response.status_code in (200, 201)
        data = response.json()
        assert len(data) == 0


class TestScenarioDetail:
    """Test scenario detail endpoints."""

    @pytest.mark.asyncio
    async def test_get_scenario_detail(
        self, client: AsyncClient, test_project, test_user
    ):
        """Test getting scenario detail."""
        # Create a scenario
        create_response = await client.post(
            "/api/v1/scenarios",
            json={
                "name": "Detail Test Scenario",
                "project_id": test_project.id,
                "creator_id": test_user.id,
            },
        )
        scenario_id = create_response.json()["id"]

        # Get detail
        response = await client.get(f"/api/v1/scenarios/{scenario_id}")
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["id"] == scenario_id
        assert data["name"] == "Detail Test Scenario"

    @pytest.mark.asyncio
    async def test_get_scenario_not_found(self, client: AsyncClient):
        """Test getting non-existent scenario."""
        response = await client.get("/api/v1/scenarios/99999")
        assert response.status_code == 404


class TestScenarioUpdate:
    """Test scenario update endpoints."""

    @pytest.mark.asyncio
    async def test_update_scenario_success(
        self, client: AsyncClient, test_project, test_user
    ):
        """Test successful scenario update."""
        # Create scenario
        create_response = await client.post(
            "/api/v1/scenarios",
            json={
                "name": "Original Name",
                "project_id": test_project.id,
                "creator_id": test_user.id,
            },
        )
        scenario_id = create_response.json()["id"]

        # Update scenario
        response = await client.put(
            f"/api/v1/scenarios/{scenario_id}",
            json={"name": "Updated Name", "priority": "P0"},
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["priority"] == "P0"


class TestScenarioDeletion:
    """Test scenario deletion endpoints."""

    @pytest.mark.asyncio
    async def test_delete_scenario_success(
        self, client: AsyncClient, test_project, test_user
    ):
        """Test successful scenario deletion."""
        # Create scenario
        create_response = await client.post(
            "/api/v1/scenarios",
            json={
                "name": "To Be Deleted",
                "project_id": test_project.id,
                "creator_id": test_user.id,
            },
        )
        scenario_id = create_response.json()["id"]

        # Delete scenario
        response = await client.delete(f"/api/v1/scenarios/{scenario_id}")
        assert response.status_code in (200, 201)

        # Verify deletion
        get_response = await client.get(f"/api/v1/scenarios/{scenario_id}")
        assert get_response.status_code == 404


class TestScenarioSteps:
    """Test scenario step management."""

    @pytest.mark.asyncio
    async def test_add_step_to_scenario(
        self, client: AsyncClient, test_project, test_user, test_keywords: list[Keyword]
    ):
        """Test adding a step to scenario."""
        # Create scenario
        create_response = await client.post(
            "/api/v1/scenarios",
            json={
                "name": "Step Test Scenario",
                "project_id": test_project.id,
                "creator_id": test_user.id,
            },
        )
        scenario_id = create_response.json()["id"]

        # Add step
        response = await client.post(
            f"/api/v1/scenarios/{scenario_id}/steps",
            json={
                "description": "New Step",
                "keyword_id": test_keywords[0].id,
                "params": {"url": "https://example.com"},
            },
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["description"] == "New Step"
        assert data["keyword_id"] == test_keywords[0].id

    @pytest.mark.asyncio
    async def test_reorder_steps(
        self, client: AsyncClient, test_project, test_user, test_keywords: list[Keyword]
    ):
        """Test reordering scenario steps."""
        # Create scenario with steps
        create_response = await client.post(
            "/api/v1/scenarios",
            json={
                "name": "Reorder Test",
                "project_id": test_project.id,
                "creator_id": test_user.id,
                "steps": [
                    {
                        "description": f"Step {i}",
                        "keyword_id": test_keywords[0].id,
                        "sort_order": i,
                    }
                    for i in range(3)
                ],
            },
        )
        scenario_id = create_response.json()["id"]
        step_ids = [step["id"] for step in create_response.json()["steps"]]

        # Reorder: reverse the order
        response = await client.put(
            f"/api/v1/scenarios/{scenario_id}/steps/reorder",
            json={"step_ids": list(reversed(step_ids))},
        )
        assert response.status_code in (200, 201)

        # Verify new order
        detail_response = await client.get(f"/api/v1/scenarios/{scenario_id}")
        steps = detail_response.json()["steps"]
        assert steps[0]["id"] == step_ids[2]
        assert steps[1]["id"] == step_ids[1]
        assert steps[2]["id"] == step_ids[0]


class TestPrePostSQL:
    """Test pre/post SQL management."""

    @pytest.mark.asyncio
    async def test_update_pre_sql(
        self, client: AsyncClient, test_project, test_user
    ):
        """Test updating pre-SQL."""
        # Create scenario
        create_response = await client.post(
            "/api/v1/scenarios",
            json={
                "name": "SQL Test",
                "project_id": test_project.id,
                "creator_id": test_user.id,
            },
        )
        scenario_id = create_response.json()["id"]

        # Update pre-SQL
        response = await client.put(
            f"/api/v1/scenarios/{scenario_id}/pre-sql",
            json={"sql": "INSERT INTO users (name) VALUES ('test');"},
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["pre_sql"] == "INSERT INTO users (name) VALUES ('test');"

    @pytest.mark.asyncio
    async def test_update_post_sql(
        self, client: AsyncClient, test_project, test_user
    ):
        """Test updating post-SQL."""
        # Create scenario
        create_response = await client.post(
            "/api/v1/scenarios",
            json={
                "name": "SQL Test",
                "project_id": test_project.id,
                "creator_id": test_user.id,
            },
        )
        scenario_id = create_response.json()["id"]

        # Update post-SQL
        response = await client.put(
            f"/api/v1/scenarios/{scenario_id}/post-sql",
            json={"sql": "DELETE FROM users WHERE name = 'test';"},
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["post_sql"] == "DELETE FROM users WHERE name = 'test';"


class TestDatasetUpload:
    """Test CSV dataset upload."""

    @pytest.mark.asyncio
    async def test_upload_csv_success(
        self, client: AsyncClient, test_project, test_user
    ):
        """Test successful CSV upload."""
        # Create scenario
        create_response = await client.post(
            "/api/v1/scenarios",
            json={
                "name": "Data Driven Test",
                "project_id": test_project.id,
                "creator_id": test_user.id,
            },
        )
        scenario_id = create_response.json()["id"]

        # Upload CSV
        csv_content = "username,password\nuser1,pass1\nuser2,pass2\n"
        files = {"file": ("test_data.csv", csv_content, "text/csv")}

        response = await client.post(
            f"/api/v1/scenarios/{scenario_id}/dataset",
            files=files,
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert "dataset" in data
        assert data["rows_count"] == 2
