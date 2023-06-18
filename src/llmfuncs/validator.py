import json
import typing

import jsonschema


def parse_json(json_string: str):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")


def validate_args_with_schema(args, schema):
    try:
        jsonschema.validate(args, schema)
        return True
    except jsonschema.ValidationError as e:
        raise ValueError(f"Failed to validate JSON: {e}")


def validate_and_call(func: typing.Callable, args_json: str, schema):
    args = parse_json(args_json)
    validate_args_with_schema(args, schema)
    return func(**args)
