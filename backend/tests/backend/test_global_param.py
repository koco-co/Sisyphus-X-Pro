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
async def test_get_global_params_grouped(async_client: AsyncClient, auth_token: str):
    """Test getting global parameters grouped by class name."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await async_client.get("/api/v1/global-functions/grouped", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "params" in data
    assert isinstance(data["params"], dict)
    # Should have built-in classes
    assert "StringUtils" in data["params"]
    assert "TimeUtils" in data["params"]
    assert "RandomUtils" in data["params"]


@pytest.mark.asyncio
async def test_create_custom_function(async_client: AsyncClient, auth_token: str):
    """Test creating a custom global parameter function."""
    headers = {"Authorization": f"Bearer {auth_token}"}
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
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["method_name"] == "test_add"
    assert data["class_name"] == "CustomUtils"
    assert data["is_builtin"] is False


@pytest.mark.asyncio
async def test_parse_function_calls(async_client: AsyncClient, auth_token: str):
    """Test parsing function calls in text."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Test simple function call
    parse_request = {
        "text": "Current time is {{current_time()}}",
        "context": {},
    }

    response = await async_client.post(
        "/api/v1/global-functions/parse",
        json=parse_request,
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "{{current_time()}}" not in data["parsed_text"]
    assert "current_time" in data["functions_called"]


@pytest.mark.asyncio
async def test_parse_nested_function_calls(async_client: AsyncClient, auth_token: str):
    """Test parsing nested function calls."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Test nested function call
    parse_request = {
        "text": "Timestamp to date: {{timestamp_to_date(current_timestamp())}}",
        "context": {},
    }

    response = await async_client.post(
        "/api/v1/global-functions/parse",
        json=parse_request,
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "timestamp_to_date" in data["functions_called"]
    assert "current_timestamp" in data["functions_called"]
    # Should not contain placeholder
    assert "{{" not in data["parsed_text"]


@pytest.mark.asyncio
async def test_parse_random_functions(async_client: AsyncClient, auth_token: str):
    """Test parsing random utility functions."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Test random functions
    parse_request = {
        "text": "Random string: {{random_string(8)}}, Random number: {{random_number(1, 100)}}",
        "context": {},
    }

    response = await async_client.post(
        "/api/v1/global-functions/parse",
        json=parse_request,
        headers=headers,
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
async def test_parse_string_functions(async_client: AsyncClient, auth_token: str):
    """Test parsing string utility functions."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Test string functions
    parse_request = {
        "text": "{{to_uppercase('hello')}} and {{to_lowercase('WORLD')}}",
        "context": {},
    }

    response = await async_client.post(
        "/api/v1/global-functions/parse",
        json=parse_request,
        headers=headers,
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
async def test_update_custom_function(async_client: AsyncClient, auth_token: str):
    """Test updating a custom function."""
    headers = {"Authorization": f"Bearer {auth_token}"}

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
        headers=headers,
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
        headers=headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["description"] == "Updated multiply function"
    assert "multiply" in data["code"]


@pytest.mark.asyncio
async def test_delete_custom_function(async_client: AsyncClient, auth_token: str):
    """Test deleting a custom function."""
    headers = {"Authorization": f"Bearer {auth_token}"}

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
        headers=headers,
    )
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    # Now delete it
    delete_response = await async_client.delete(
        f"/api/v1/global-functions/{created_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204

    # Verify it's deleted
    get_response = await async_client.get(
        f"/api/v1/global-functions/{created_id}",
        headers=headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_cannot_modify_builtin_function(async_client: AsyncClient, auth_token: str):
    """Test that built-in functions cannot be modified."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Try to get a built-in function
    list_response = await async_client.get(
        "/api/v1/global-functions?is_builtin=true", headers=headers
    )
    assert list_response.status_code == 200

    builtins = list_response.json()["items"]
    if builtins:
        builtin_id = builtins[0]["id"]

        # Try to update
        update_response = await async_client.put(
            f"/api/v1/global-functions/{builtin_id}",
            json={"description": "Hacked"},
            headers=headers,
        )
        assert update_response.status_code == 403

        # Try to delete
        delete_response = await async_client.delete(
            f"/api/v1/global-functions/{builtin_id}", headers=headers
        )
        assert delete_response.status_code == 403
