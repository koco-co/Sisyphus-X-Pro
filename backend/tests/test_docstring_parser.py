"""Tests for docstring parser utility."""

import pytest

from app.utils.docstring_parser import parse_docstring


@pytest.mark.parametrize(
    "code,expected_name,expected_params",
    [
        # Google style docstring
        (
            '''
def http_request(url: str, method: str = "GET", **kwargs) -> dict:
    """
    Send HTTP request.

    Args:
        url: Request URL
        method: HTTP method (default: GET)
        **kwargs: Additional arguments

    Returns:
        Response dict
    """
    pass
''',
            "http_request",
            ["url", "method"],
        ),
        # NumPy style docstring
        (
            '''
def db_query(connection, sql: str, fetch_one: bool = False):
    """
    Execute database query.

    Parameters
    ----------
    connection : DatabaseConnection
        Database connection object
    sql : str
        SQL query string
    fetch_one : bool, optional
        Fetch only one record (default: False)

    Returns
    -------
    list or dict
        Query results
    """
    pass
''',
            "db_query",
            ["connection", "sql", "fetch_one"],
        ),
        # Simple docstring
        (
            '''
def simple_func(param1, param2):
    """A simple function.

    Args:
        param1: First parameter
        param2: Second parameter

    Returns:
        Nothing
    """
    pass
''',
            "simple_func",
            ["param1", "param2"],
        ),
    ],
)
def test_parse_docstring_various_formats(code, expected_name, expected_params):
    """Test parsing various docstring formats."""
    result = parse_docstring(code)

    assert result["error"] is None
    assert result["function_name"] == expected_name

    param_names = [p["name"] for p in result["params"]]
    # Filter out kwargs from comparison
    param_names_filtered = [n for n in param_names if n != "kwargs"]
    assert param_names_filtered == expected_params


def test_parse_docstring_extracts_descriptions():
    """Test that parameter descriptions are extracted correctly."""
    code = '''
def my_function(name: str, count: int = 5):
    """
    Process items.

    Args:
        name: The name to process
        count: Number of times to repeat

    Returns:
        Processing result
    """
    pass
'''

    result = parse_docstring(code)

    assert result["function_name"] == "my_function"

    # Find name parameter
    name_param = next((p for p in result["params"] if p["name"] == "name"), None)
    assert name_param is not None
    assert name_param["description"] == "The name to process"
    assert name_param["type"] == "str"
    assert name_param["default"] is None

    # Find count parameter
    count_param = next((p for p in result["params"] if p["name"] == "count"), None)
    assert count_param is not None
    assert count_param["description"] == "Number of times to repeat"
    assert count_param["type"] == "int"
    assert count_param["default"] == "5"


def test_parse_docstring_handles_kwargs():
    """Test handling of **kwargs."""
    code = '''
def func_with_kwargs(required_param, **kwargs):
    """
    Function with keyword arguments.

    Args:
        required_param: This is required
        **kwargs: Additional keyword arguments
    """
    pass
'''

    result = parse_docstring(code)

    param_names = [p["name"] for p in result["params"]]
    assert "required_param" in param_names
    assert "kwargs" in param_names

    kwargs_param = next((p for p in result["params"] if p["name"] == "kwargs"), None)
    assert kwargs_param is not None
    assert kwargs_param["default"] == "**kwargs"


def test_parse_docstring_handles_invalid_code():
    """Test handling of invalid Python code."""
    result = parse_docstring("def invalid syntax here(")

    assert result["error"] is not None
    assert "Syntax error" in result["error"]


def test_parse_docstring_handles_no_function():
    """Test handling of code without function definition."""
    result = parse_docstring("x = 42")

    assert result["error"] is not None
    assert "No function definition found" in result["error"]


def test_parse_docstring_function_without_docstring():
    """Test handling of function without docstring."""
    code = '''
def no_docstring(param1, param2):
    pass
'''

    result = parse_docstring(code)

    assert result["function_name"] == "no_docstring"
    assert result["description"] == ""
    # Should still extract params from signature
    param_names = [p["name"] for p in result["params"]]
    assert param_names == ["param1", "param2"]


def test_parse_docstring_builtin_keyword():
    """Test parsing of built-in http_request keyword."""
    from app.builtin_keywords import BUILTIN_KEYWORDS

    http_request = next(k for k in BUILTIN_KEYWORDS if k["method_name"] == "http_request")

    result = parse_docstring(http_request["code"])

    assert result["function_name"] == "http_request"
    assert len(result["params"]) > 3
    assert result["description"] != ""

    # Check url parameter
    url_param = next((p for p in result["params"] if p["name"] == "url"), None)
    assert url_param is not None
    assert "URL" in url_param["description"]
