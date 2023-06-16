import inspect
from typing import get_type_hints
import docstring_parser


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
    doc_parsed = docstring_parser.parse(inspect.getdoc(func))
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
        # Get parameter description from parsed docstring
        param_doc = next(
            (p.description for p in doc_parsed.params if p.arg_name == param_name), '')
        # Add information about default value
        if param.default is not param.empty:
            param_doc += f' A sane default value might be {param.default}.'
        param_schema = {
            "type": param_type_str,
            "description": param_doc,
        }
        params_schema[param_name] = param_schema

    return {
        "name": name,
        "description": doc_parsed.short_description,
        "parameters": {
            "type": "object",
            "properties": params_schema,
            # "required": TODO
        }
    }
