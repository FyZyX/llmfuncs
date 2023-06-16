import inspect
from typing import get_type_hints


def schema_from_module(module):
    """Extracts function information from a Python module and formats it into a schema."""
    schemas = []
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            schema = function_to_schema(name, obj)
            schemas.append(schema)
    return schemas


def function_to_schema(name, func):
    """Converts a function into a schema."""
    doc = inspect.getdoc(func)
    signature = inspect.signature(func)
    parameters = signature.parameters
    type_hints = get_type_hints(func)
    params_schema = {}

    for param_name, param in parameters.items():
        if param_name not in type_hints:
            # We could skip parameters without type hints, or treat them as any type
            continue
        param_type = type_hints[param_name]
        param_type_str = str(param_type)
        # TODO: convert Python type to JSON Schema type
        # TODO: parse docstring to get parameter descriptions
        param_schema = {
            "type": param_type_str,
            # "description": TODO,
        }
        params_schema[param_name] = param_schema

    return {
        "name": name,
        "description": doc,
        "parameters": {
            "type": "object",
            "properties": params_schema,
            # "required": TODO
        }
    }
