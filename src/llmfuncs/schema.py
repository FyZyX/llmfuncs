import glob
import importlib
import importlib.util
import inspect
import pathlib
import pkgutil
import types
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

    if origin is tuple or origin is typing.Tuple:
        return {"type": "array",
                "items": [_python_type_to_json_schema_type(arg) for arg in args]}

    if origin is list or origin is typing.List:
        # For simplicity, we're assuming all elements in the list are of the same type
        return {"type": "array", "items": _python_type_to_json_schema_type(args[0])}

    if origin is set or origin is typing.Set:
        return {"type": "array", "uniqueItems": True,
                "items": _python_type_to_json_schema_type(args[0])}

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

    param_schema = {
        "type": param_type_str,
        "description": param_doc,
    }

    if param.default is not param.empty:
        param_schema["default"] = param.default

    return param_schema


def from_function(func: typing.Callable, include_return=False):
    """Converts a function into a schema."""
    func_name = func.__name__
    doc = inspect.getdoc(func)
    if not doc:
        raise ValueError(f"Missing docstring for function '{func_name}'")
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
        "name": func_name,
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


def from_module(module: str | pathlib.Path | types.ModuleType, include_return=False):
    """
    Extracts function information from a Python module and formats it into a schema.
    The function can accept either a module object or a string.
    If a string is passed, it is considered a path and the function will attempt to
    create a module object without executing the module's code.
    """
    schemas = []

    # If a string is passed in, create a module object without executing the code
    if isinstance(module, str):
        spec = importlib.util.spec_from_file_location(module, module)
        module = importlib.util.module_from_spec(spec)

    # Check if the module is a proper module
    if not isinstance(module, types.ModuleType):
        raise ValueError("Argument must be a module or the path to a module")

    for _, func in inspect.getmembers(module, inspect.isfunction):
        schema = from_function(func, include_return=include_return)
        schemas.append(schema)

    return schemas


def from_package(package: str | pathlib.Path | types.ModuleType, include_return=False):
    """Extracts function information from all modules in a Python package and formats it into schemas."""
    schemas = []
    if isinstance(package, str):
        package = importlib.import_module(package)
    for importer, module_name, _ in pkgutil.walk_packages(package.__path__):
        module_path = f'{package.__name__}.{module_name}'
        schemas.append(from_module(module_path, include_return))
    return schemas


def from_glob(pattern: str):
    """
    Given a glob pattern, find all the Python modules that match the pattern,
    and collect the schemas from all those modules.
    """
    schemas = []
    for filename in glob.glob(pattern):
        path = pathlib.Path(filename)
        # We only want to process Python files
        if not path.suffix == ".py":
            continue
        # Normalize the filename to an absolute path
        module_schemas = from_module(path.absolute())
        schemas.extend(module_schemas)
    return schemas
