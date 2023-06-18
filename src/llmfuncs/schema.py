import inspect
import typing

import docstring_parser

JsonSchema = typing.Union[
    typing.Dict[str, "JSONType"],
    typing.List["JSONType"],
    str,
    int,
    float,
    bool,
    None,
]


def json_schema_type(py_type: typing.Any) -> JsonSchema:
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
            return json_schema_type(args[0])
        else:
            return [json_schema_type(arg) for arg in args]

    if origin is tuple or origin is typing.Tuple:
        return {"type": "array",
                "items": [json_schema_type(arg) for arg in args]}

    if origin is list or origin is typing.List:
        # For simplicity, we're assuming all elements in the list are of the same type
        return {"type": "array", "items": json_schema_type(args[0])}

    if origin is set or origin is typing.Set:
        return {"type": "array", "uniqueItems": True,
                "items": json_schema_type(args[0])}

    if origin is dict or origin is typing.Dict:
        # For simplicity, we're assuming all keys are strings
        # and all values are of the same type
        additional_properties = json_schema_type(args[1])
        return {"type": "object", "additionalProperties": additional_properties}

    # The type is not supported
    raise ValueError(f"Cannot convert {py_type} to a JSON schema type")


def get_param_schema(
        param_name: str,
        param: inspect.Parameter,
        type_hints: typing.Dict[str, typing.Any],
        doc_parsed: docstring_parser.Docstring,
) -> JsonSchema:
    """Create a schema for a single parameter."""
    if param_name not in type_hints:
        raise ValueError(f"Missing type hint for parameter '{param_name}'")
    param_type = type_hints[param_name]
    param_type_str = json_schema_type(param_type)
    descriptions = (p.description for p in doc_parsed.params
                    if p.arg_name == param_name)
    param_doc = next(descriptions, None)
    if param_doc is None:
        raise ValueError(
            f"Missing description for parameter '{param_name}' in docstring")

    param_schema = {
        "type": param_type_str,
        "description": param_doc,
    }

    if param.default is not param.empty:
        param_schema["default"] = param.default

    return param_schema
