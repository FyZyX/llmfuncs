import json

import jsonschema


def parse_json(json_string):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")


def call_function_with_validation(schema, func, json_string):
    args = parse_json(json_string)
    try:
        jsonschema.validate(args, schema)
    except jsonschema.ValidationError as e:
        raise ValueError(f"Failed to validate JSON: {e}")
    return func(**args)
