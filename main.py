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


def python_type_to_json_schema_type(py_type):
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


def function_to_schema(name, func):
    """Converts a function into a schema."""
    doc_parsed = docstring_parser.parse(inspect.getdoc(func))
    signature = inspect.signature(func)
    parameters = signature.parameters
    type_hints = get_type_hints(func)
    params_schema = {}
    required_params = []

    for param_name, param in parameters.items():
        if param_name not in type_hints:
            continue
        param_type = type_hints[param_name]
        param_type_str = python_type_to_json_schema_type(param_type)
        param_doc = next(
            (p.description for p in doc_parsed.params if p.arg_name == param_name), '')
        if param.default is param.empty:
            required_params.append(param_name)
        else:
            param_doc += f' A sane default value might be {param.default}.'
        params_schema[param_name] = {
            "type": param_type_str,
            "description": param_doc,
        }

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
