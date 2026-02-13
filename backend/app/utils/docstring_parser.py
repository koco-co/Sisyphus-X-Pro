"""Parse Python function docstrings to extract parameter information."""

import ast
import inspect
import re
from typing import Any


def parse_docstring(code: str) -> dict[str, Any]:
    """Parse Python code docstring to extract function info.

    Args:
        code: Python source code containing a function with docstring

    Returns:
        Dictionary with:
        - function_name: Extracted function name
        - params: List of parameter dicts with keys:
            - name: Parameter name
            - type: Parameter type (if available in signature)
            - description: From docstring
            - default: Default value (if any)
        - description: Function description from docstring
        - error: Error message if parsing failed

    Raises:
        ValueError: If code is invalid or no function found
    """
    result = {
        "function_name": None,
        "params": [],
        "description": "",
        "error": None,
    }

    try:
        # Parse the code
        tree = ast.parse(code)

        # Find the first function definition
        func_def = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_def = node
                break

        if not func_def:
            result["error"] = "No function definition found in code"
            return result

        result["function_name"] = func_def.name

        # Extract docstring
        docstring = ast.get_docstring(func_def) or ""

        # Parse docstring
        params_from_docstring = _parse_docstring_params(docstring)
        result["description"] = _extract_function_description(docstring)

        # Extract parameter info from function signature
        params_from_signature = _extract_signature_params(func_def)

        # Merge signature and docstring info
        for param_name, param_info in params_from_signature.items():
            param_data = {
                "name": param_name,
                "type": param_info.get("type"),
                "default": param_info.get("default"),
                "description": params_from_docstring.get(param_name, ""),
            }
            result["params"].append(param_data)

    except SyntaxError as e:
        result["error"] = f"Syntax error in code: {str(e)}"
    except Exception as e:
        result["error"] = f"Error parsing code: {str(e)}"

    return result


def _parse_docstring_params(docstring: str) -> dict[str, str]:
    """Extract parameter descriptions from docstring.

    Supports both Google and NumPy style docstrings.

    Args:
        docstring: Function docstring

    Returns:
        Dict mapping parameter names to descriptions
    """
    params = {}

    # Google style: Args: param_name: description
    google_pattern = r"Args:\s*\n((?:\s+\w+:\s*.*?\n)*)"
    google_match = re.search(google_pattern, docstring)

    if google_match:
        args_block = google_match.group(1)
        # Match each parameter line (excluding **kwargs)
        # Each param is on its own line: name: description
        lines = args_block.split("\n")
        current_param = None
        current_desc = []

        for line in lines:
            # Check if line starts a new parameter (indented param_name:)
            param_match = re.match(r"\s+(\w+):\s*(.*)", line)
            if param_match:
                # Save previous parameter if exists
                if current_param and current_param != "kwargs":
                    params[current_param] = " ".join(current_desc).strip()

                # Start new parameter
                current_param = param_match.group(1)
                desc_part = param_match.group(2).strip()
                current_desc = [desc_part] if desc_part else []
            elif current_param and current_param != "kwargs":
                # Continuation of previous parameter's description
                stripped = line.strip()
                if stripped:
                    current_desc.append(stripped)

        # Save last parameter
        if current_param and current_param != "kwargs" and current_desc:
            params[current_param] = " ".join(current_desc).strip()

    # NumPy style: Parameters ---------- param_name type description
    if not params:
        numpy_pattern = r"Parameters\s*-+\s*((?:\s+\w+.*?\n)*)"
        numpy_match = re.search(numpy_pattern, docstring)

        if numpy_match:
            params_block = numpy_match.group(1)
            # Match each parameter line
            for match in re.finditer(r"(\w+)\s*(?:\((.*?)\))?\s*(.*?)(?=\n\s*\w|\Z)", params_block, re.DOTALL):
                param_name = match.group(1)
                description = match.group(3).strip()
                if param_name and description:
                    params[param_name] = description

    return params


def _extract_function_description(docstring: str) -> str:
    """Extract function description (first line or paragraph).

    Args:
        docstring: Function docstring

    Returns:
        Description text
    """
    # Remove Args/Parameters/Returns sections
    sections_pattern = r"(?:Args:|Parameters:|Returns:|Raises:)"
    parts = re.split(sections_pattern, docstring, maxsplit=1)
    description = parts[0].strip()

    # Clean up
    description = re.sub(r'\s+', ' ', description)
    return description


def _extract_signature_params(func_def: ast.FunctionDef) -> dict[str, dict[str, Any]]:
    """Extract parameter information from function signature.

    Args:
        func_def: AST FunctionDef node

    Returns:
        Dict mapping parameter names to type and default info
    """
    params = {}

    for arg in func_def.args.args:
        # Skip self
        if arg.arg == "self":
            continue

        param_info = {"type": None, "default": None}

        # Get type annotation
        if arg.annotation:
            param_info["type"] = _unparse_type(arg.annotation)

        # Check if parameter has default value
        defaults_start = len(func_def.args.args) - len(func_def.args.defaults)
        arg_index = func_def.args.args.index(arg)
        if arg_index >= defaults_start:
            default_index = arg_index - defaults_start
            param_info["default"] = _unparse_ast(func_def.args.defaults[default_index])
        else:
            # No default means it's required
            param_info["default"] = None

        params[arg.arg] = param_info

    # Handle **kwargs
    if func_def.args.kwarg:
        params[func_def.args.kwarg.arg] = {"type": None, "default": "**kwargs"}

    return params


def _unparse_type(node: ast.AST) -> str:
    """Convert AST type annotation to string.

    Args:
        node: AST node representing type

    Returns:
        String representation of type
    """
    try:
        # Python 3.9+ has ast.unparse
        if hasattr(ast, "unparse"):
            return ast.unparse(node)
        else:
            # Fallback for older Python
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Subscript):
                value = _unparse_type(node.value)
                slice_val = _unparse_type(node.slice)
                return f"{value}[{slice_val}]"
            else:
                return str(type(node).__name__)
    except Exception:
        return None


def _unparse_ast(node: ast.AST) -> Any:
    """Convert AST literal node to Python value.

    Args:
        node: AST node

    Returns:
        Python value
    """
    try:
        if hasattr(ast, "unparse"):
            return ast.unparse(node)
        else:
            # Fallback: handle common cases
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.List):
                return [_unparse_ast(e) for e in node.elts]
            elif isinstance(node, ast.Dict):
                return {
                    _unparse_ast(k): _unparse_ast(v)
                    for k, v in zip(node.keys, node.values)
                }
            else:
                return None
    except Exception:
        return None
