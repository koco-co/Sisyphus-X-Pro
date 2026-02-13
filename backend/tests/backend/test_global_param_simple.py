"""Simple tests for global parameter functionality."""

import pytest


@pytest.mark.asyncio
async def test_builtin_functions_initialized(async_client):
    """Test that built-in functions are initialized on startup."""
    # In development mode, auth is bypassed
    response = await async_client.get("/api/v1/global-functions/grouped")

    assert response.status_code == 200
    data = response.json()
    assert "params" in data
    # Should have built-in classes
    assert "StringUtils" in data["params"]
    assert "TimeUtils" in data["params"]
    assert "RandomUtils" in data["params"]


@pytest.mark.asyncio
async def test_parse_simple_function_call(async_client):
    """Test parsing simple function call."""
    request_data = {
        "text": "Current time: {{current_time()}}",
        "context": {},
    }

    response = await async_client.post("/api/v1/global-functions/parse", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "current_time" in data["functions_called"]
    # Placeholder should be replaced
    assert "{{current_time()}}" not in data["parsed_text"]


@pytest.mark.asyncio
async def test_parse_nested_function_call(async_client):
    """Test parsing nested function call."""
    request_data = {
        "text": "Date: {{timestamp_to_date(current_timestamp())}}",
        "context": {},
    }

    response = await async_client.post("/api/v1/global-functions/parse", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "timestamp_to_date" in data["functions_called"]
    assert "current_timestamp" in data["functions_called"]
    # No placeholders should remain
    assert "{{" not in data["parsed_text"]


@pytest.mark.asyncio
async def test_parse_string_functions(async_client):
    """Test string utility functions."""
    request_data = {
        "text": "{{to_uppercase('hello')}} and {{to_lowercase('WORLD')}}",
        "context": {},
    }

    response = await async_client.post("/api/v1/global-functions/parse", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "HELLO" in data["parsed_text"]
    assert "world" in data["parsed_text"]


@pytest.mark.asyncio
async def test_parse_random_functions(async_client):
    """Test random utility functions."""
    request_data = {
        "text": "Random: {{random_string(8)}}, {{random_number(1, 100)}}",
        "context": {},
    }

    response = await async_client.post("/api/v1/global-functions/parse", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Placeholders replaced
    assert "{{random_string" not in data["parsed_text"]
    assert "{{random_number" not in data["parsed_text"]
