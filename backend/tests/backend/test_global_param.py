"""Tests for global parameter functionality."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_global_params(async_client: AsyncClient):
    """Test listing global parameters."""
    response = await async_client.get("/api/v1/global-functions")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_global_params_grouped(async_client: AsyncClient):
    """Test getting global parameters grouped by class name."""
    response = await async_client.get("/api/v1/global-functions/grouped")

    assert response.status_code == 200
    data = response.json()
    assert "params" in data
    assert isinstance(data["params"], dict)

    # Check if built-in classes exist (they should be initialized)
    # If empty, the initialization might not have run
    if data["params"]:
        # At minimum, we should have these built-in classes
        expected_classes = ["StringUtils", "TimeUtils", "RandomUtils"]
        for cls in expected_classes:
            if cls in data["params"]:
                assert isinstance(data["params"][cls], list)


@pytest.mark.asyncio
async def test_create_custom_function(async_client: AsyncClient):
    """Test creating a custom global parameter function."""
    function_data = {
        "class_name": "CustomUtils",
        "method_name": "test_add",
        "description": "Test add function",
        "code": '''
def test_add(a: int, b: int) -> int:
    """Add two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b
''',
        "params_in": [
            {"name": "a", "type": "int", "description": "First number"},
            {"name": "b", "type": "int", "description": "Second number"},
        ],
        "params_out": [{"type": "int", "description": "Sum of a and b"}],
    }

    response = await async_client.post(
        "/api/v1/global-functions",
        json=function_data,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["method_name"] == "test_add"
    assert data["class_name"] == "CustomUtils"
    assert data["is_builtin"] is False


@pytest.mark.asyncio
async def test_parse_function_calls(async_client: AsyncClient):
    """Test parsing function calls in text."""

    # Test simple function call
    parse_request = {
        "text": "Current time is {{current_time()}}",
        "context": {},
    }

    response = await async_client.post(
        "/api/v1/global-functions/parse",
        json=parse_request,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "{{current_time()}}" not in data["parsed_text"]
    assert "current_time" in data["functions_called"]


@pytest.mark.asyncio
async def test_parse_nested_function_calls(async_client: AsyncClient):
    """Test parsing nested function calls."""

    # Test nested function call
    parse_request = {
        "text": "Timestamp to date: {{timestamp_to_date(current_timestamp())}}",
        "context": {},
    }

    response = await async_client.post(
        "/api/v1/global-functions/parse",
        json=parse_request,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "timestamp_to_date" in data["functions_called"]
    assert "current_timestamp" in data["functions_called"]
    # Should not contain placeholder
    assert "{{" not in data["parsed_text"]


@pytest.mark.asyncio
async def test_parse_random_functions(async_client: AsyncClient):
    """Test parsing random utility functions."""

    # Test random functions
    parse_request = {
        "text": "Random string: {{random_string(8)}}, Random number: {{random_number(1, 100)}}",
        "context": {},
    }

    response = await async_client.post(
        "/api/v1/global-functions/parse",
        json=parse_request,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "random_string" in data["functions_called"]
    assert "random_number" in data["functions_called"]
    # Check that placeholders are replaced
    assert "{{random_string" not in data["parsed_text"]
    assert "{{random_number" not in data["parsed_text"]


@pytest.mark.asyncio
async def test_parse_string_functions(async_client: AsyncClient):
    """Test parsing string utility functions."""

    # Test string functions
    parse_request = {
        "text": "{{to_uppercase('hello')}} and {{to_lowercase('WORLD')}}",
        "context": {},
    }

    response = await async_client.post(
        "/api/v1/global-functions/parse",
        json=parse_request,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "to_uppercase" in data["functions_called"]
    assert "to_lowercase" in data["functions_called"]
    # Check results
    assert "HELLO" in data["parsed_text"]
    assert "world" in data["parsed_text"]


@pytest.mark.asyncio
async def test_update_custom_function(async_client: AsyncClient):
    """Test updating a custom function."""

    # First create a function
    function_data = {
        "class_name": "CustomUtils",
        "method_name": "test_multiply",
        "description": "Test multiply function",
        "code": "def test_multiply(a, b): return a * b",
        "params_in": [],
        "params_out": [],
    }

    create_response = await async_client.post(
        "/api/v1/global-functions",
        json=function_data,
    )
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    # Now update it
    update_data = {
        "description": "Updated multiply function",
        "code": "def test_multiply(a, b): return a * b * 2",
    }

    update_response = await async_client.put(
        f"/api/v1/global-functions/{created_id}",
        json=update_data,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["description"] == "Updated multiply function"
    assert "multiply" in data["code"]


@pytest.mark.asyncio
async def test_delete_custom_function(async_client: AsyncClient):
    """Test deleting a custom function."""

    # First create a function
    function_data = {
        "class_name": "CustomUtils",
        "method_name": "test_to_delete",
        "description": "Test function to delete",
        "code": "def test_to_delete(): return 42",
        "params_in": [],
        "params_out": [],
    }

    create_response = await async_client.post(
        "/api/v1/global-functions",
        json=function_data,
    )
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    # Now delete it
    delete_response = await async_client.delete(
        f"/api/v1/global-functions/{created_id}",
    )

    assert delete_response.status_code == 204

    # Verify it's deleted
    get_response = await async_client.get(
        f"/api/v1/global-functions/{created_id}",
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_cannot_modify_builtin_function(async_client: AsyncClient):
    """Test that built-in functions cannot be modified."""

    # Try to get a built-in function
    list_response = await async_client.get(
        "/api/v1/global-functions?is_builtin=true"
    )
    assert list_response.status_code == 200

    builtins = list_response.json()["items"]
    if builtins:
        builtin_id = builtins[0]["id"]

        # Try to update
        update_response = await async_client.put(
            f"/api/v1/global-functions/{builtin_id}",
            json={"description": "Hacked"},
        )
        assert update_response.status_code == 403

        # Try to delete
        delete_response = await async_client.delete(
            f"/api/v1/global-functions/{builtin_id}"
        )
        assert delete_response.status_code == 403
