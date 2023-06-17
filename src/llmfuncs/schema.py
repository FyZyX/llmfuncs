import inspect
import typing

import docstring_parser


def _python_type_to_json_schema_type(py_type):
    mapping = {
        int: "integer",
        float: "number",
        bool: "boolean",
        str: "string",
        type(None): "null",
    }

    # Check if type is a basic type
    if py_type in mapping:
        return mapping[py_type]

    origin = typing.get_origin(py_type)
    args = typing.get_args(py_type)

    if origin is typing.Union:
        # this is a special case to handle Optional[type] which is just syntactic sugar
        # around Union[type, None]
        if len(args) == 2 and type(None) in args:
            # Assuming the None is always last
            return _python_type_to_json_schema_type(args[0])
        else:
            return [_python_type_to_json_schema_type(arg) for arg in args]

    if origin is list or origin is typing.List:
        # For simplicity, we're assuming all elements in the list are of the same type
        return {"type": "array", "items": _python_type_to_json_schema_type(args[0])}

    if origin is dict or origin is typing.Dict:
        # For simplicity, we're assuming all keys are strings
        # and all values are of the same type
        additional_properties = _python_type_to_json_schema_type(args[1])
        return {"type": "object", "additionalProperties": additional_properties}

    # The type is not supported
    raise ValueError(f"Cannot convert {py_type} to a JSON schema type")


def _get_param_schema(param_name, param, type_hints, doc_parsed):
    """Create a schema for a single parameter."""
    if param_name not in type_hints:
        raise ValueError(f"Missing type hint for parameter '{param_name}'")
    param_type = type_hints[param_name]
    param_type_str = _python_type_to_json_schema_type(param_type)
    descriptions = (p.description for p in doc_parsed.params
                    if p.arg_name == param_name)
    param_doc = next(descriptions, None)
    if param_doc is None:
        raise ValueError(
            f"Missing description for parameter '{param_name}' in docstring")
    if param.default is not param.empty:
        param_doc += f' A sane default value might be {param.default}.'
    return {
        "type": param_type_str,
        "description": param_doc,
    }


def from_function(name, func, include_return=False):
    """Converts a function into a schema."""
    doc = inspect.getdoc(func)
    if not doc:
        raise ValueError(f"Missing docstring for function '{name}'")
    doc_parsed = docstring_parser.parse(doc)
    signature = inspect.signature(func)
    parameters = signature.parameters
    type_hints = typing.get_type_hints(func)
    params_schema = {}
    required_params = []

    for param_name, param in parameters.items():
        param_schema = _get_param_schema(param_name, param, type_hints, doc_parsed)
        params_schema[param_name] = param_schema
        if param.default is param.empty:
            required_params.append(param_name)

    schema = {
        "name": name,
        "description": doc_parsed.short_description,
        "parameters": {
            "type": "object",
            "properties": params_schema,
        },
    }

    if required_params:
        schema["parameters"]["required"] = required_params

    if include_return and signature.return_annotation is not signature.empty:
        schema["return"] = _python_type_to_json_schema_type(signature.return_annotation)

    return schema


def from_module(module):
    """Extracts function information from a Python module and formats it into a schema."""
    schemas = []
    for name, func in inspect.getmembers(module, inspect.isfunction):
        schema = from_function(name, func)
        schemas.append(schema)
    return schemas
