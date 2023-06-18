import glob
import importlib.util
import inspect
import pathlib
import pkgutil
import types
import typing

import docstring_parser

from . import schema, validator


class Tool:
    def __init__(self, func: typing.Callable, include_return=False):
        self._func = func
        self._include_return = include_return

        doc = inspect.getdoc(func)
        if not doc:
            raise ValueError(f"Missing docstring for function '{self.name()}'")

        self._docstring = docstring_parser.parse(doc)
        self._signature = inspect.signature(func)
        self._type_hints = typing.get_type_hints(func)
        self._params_schema = {}
        self._required_params = []

        self._parse_arguments()

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)

    def _parse_arguments(self):
        for param_name, param in self._signature.parameters.items():
            param_schema = schema.get_param_schema(
                param_name, param, self._type_hints, self._docstring,
            )
            self._params_schema[param_name] = param_schema
            if param.default is param.empty:
                self._required_params.append(param_name)

    def _has_return(self):
        return self._signature.return_annotation is not self._signature.empty

    def name(self) -> str:
        return self._func.__name__

    def schema(self):
        func_schema = {
            "name": self.name(),
            "description": self._docstring.short_description,
            "parameters": {
                "type": "object",
                "properties": self._params_schema,
            },
        }

        if self._required_params:
            func_schema["parameters"]["required"] = self._required_params

        if self._include_return and self._has_return():
            schema_type = schema.json_schema_type(self._signature.return_annotation)
            func_schema["return"] = schema_type

        return func_schema


class ToolCollection:
    def __init__(self, tools: typing.List[Tool] = None):
        self._tools: typing.Dict[str, Tool] = {}
        for tool in tools or []:
            self.add_tool(tool)

    def __len__(self):
        return len(self._tools)

    def add_tool(self, tool: Tool):
        self._tools[tool.name()] = tool

    def add_tools_from_module(
            self,
            module: str | pathlib.Path | types.ModuleType,
            include_return: bool = False,
    ):
        """
        Extracts function information from a Python module and formats it into a schema.
        The function can accept either a module object or a string.
        If a string is passed, it is considered a path and the function will attempt to
        create a module object without executing the module's code.
        """
        # If a string is passed in, create a module object without executing the code
        if isinstance(module, str):
            spec = importlib.util.spec_from_file_location(module, module)
            module = importlib.util.module_from_spec(spec)

        # Check if the module is a proper module
        if not isinstance(module, types.ModuleType):
            raise ValueError("Argument must be a module or the path to a module")

        for _, func in inspect.getmembers(module, inspect.isfunction):
            tool = Tool(func, include_return=include_return)
            self.add_tool(tool)

    def add_tools_from_package(
            self,
            package: str | pathlib.Path | types.ModuleType,
            include_return: bool = False,
    ):
        """Extracts and formats function schemas for all modules in a package."""
        if isinstance(package, str):
            package = importlib.import_module(package)
        for _, module_name, _ in pkgutil.walk_packages(package.__path__):
            module_path = f"{package.__name__}.{module_name}"
            self.add_tools_from_module(module_path, include_return=include_return)

    def add_tools_from_glob(self, pattern: str):
        """
        Given a glob pattern, find all the Python modules that match the pattern,
        and collect the schemas from all those modules.
        """
        for filename in glob.glob(pattern):
            path = pathlib.Path(filename)
            # We only want to process Python files
            if not path.suffix == ".py":
                continue
            # Normalize the filename to an absolute path
            self.add_tools_from_module(path.absolute())

    def use_tool(self, tool_name: str, json_args: str | typing.Mapping) -> typing.Any:
        tool = self._tools.get(tool_name)
        if not tool:
            raise ValueError(f"No tool found with name: {tool_name}")

        params_schema = tool.schema()["parameters"]
        is_string = isinstance(json_args, str)
        args = validator.parse_json(json_args) if is_string else json_args
        validator.validate_args_with_schema(args, params_schema)
        return tool(**args)

    def schema(self) -> typing.List[schema.JsonSchema]:
        return [tool.schema() for tool in self._tools.values()]
