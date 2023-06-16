import inspect
from typing import get_type_hints
import docstring_parser


def _python_type_to_json_schema_type(py_type):
    mapping = {
        int: "integer",
        float: "number",
        bool: "boolean",
        str: "string",
        type(None): "null",
        list: "array",
        dict: "object",
    }
    return mapping.get(py_type, "any")


def _get_param_schema(param_name, param, type_hints, doc_parsed):
    """Create a schema for a single parameter."""
    if param_name not in type_hints:
        return None
    param_type = type_hints[param_name]
    param_type_str = _python_type_to_json_schema_type(param_type)
    descriptions = (p.description for p in doc_parsed.params
                    if p.arg_name == param_name)
    param_doc = next(descriptions, '')
    if param.default is not param.empty:
        param_doc += f' A sane default value might be {param.default}.'
    return {
        "type": param_type_str,
        "description": param_doc,
    }


def from_function(name, func):
    """Converts a function into a schema."""
    doc_parsed = docstring_parser.parse(inspect.getdoc(func))
    signature = inspect.signature(func)
    parameters = signature.parameters
    type_hints = get_type_hints(func)
    params_schema = {}
    required_params = []

    for param_name, param in parameters.items():
        param_schema = _get_param_schema(param_name, param, type_hints, doc_parsed)
        if param_schema is not None:
            params_schema[param_name] = param_schema
            if param.default is param.empty:
                required_params.append(param_name)

    schema = {
        "name": name,
        "description": doc_parsed.short_description,
        "parameters": {
            "type": "object",
            "properties": params_schema,
        }
    }

    if required_params:
        schema["parameters"]["required"] = required_params

    return schema


def from_module(module):
    """Extracts function information from a Python module and formats it into a schema."""
    schemas = []
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            schema = from_function(name, obj)
            schemas.append(schema)
    return schemas
