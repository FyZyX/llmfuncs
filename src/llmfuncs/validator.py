import json
import typing

import jsonschema

from . import schema


def parse_json(json_string: str) -> schema.JsonSchema:
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")


def validate_args_with_schema(args: typing.Iterable, func_schema: schema.JsonSchema):
    try:
        jsonschema.validate(args, func_schema)
        return True
    except jsonschema.ValidationError as e:
        raise ValueError(f"Failed to validate JSON: {e}")
