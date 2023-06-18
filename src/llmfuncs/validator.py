import jsonschema


def call_function_with_validation(schema, func, args):
    jsonschema.validate(args, schema)
    return func(**args)
