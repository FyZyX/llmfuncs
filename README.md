# llmfuncs

`llmfuncs` is a Python package for documenting, managing, and validating Python functions based on their signature and docstrings. It automatically generates JSON Schema for functions, and provides a way to validate function arguments against the schema.

## Features

- Automatic generation of JSON Schema from Python function signature and docstrings.
- Support for Python built-in types and many typing module types.
- Use and validate functions with JSON arguments against their schema.
- Management of multiple functions through a ToolCollection object.
- Bulk addition of functions from a module, a package, or a glob pattern.
- Simple and intuitive API.

## Installation

Install `llmfuncs` using pip:

```shell
pip install llmfuncs
```

## Usage

### Tool

The `Tool` class encapsulates a function and its associated schema.

```python
from llmfuncs.tool import Tool

def greet(name: str) -> str:
    """Greet someone.

    Args:
        name: Name of the person to greet.

    Returns:
        A greeting message.
    """
    return f"Hello, {name}!"

tool = Tool(greet)
print(tool.name())  # "greet"
print(tool.schema())
```

### ToolCollection

The `ToolCollection` class is a container for multiple `Tool` objects. It provides methods to add tools and use them.

```python
from llmfuncs.tool import Tool, ToolCollection

tool_collection = ToolCollection()
tool_collection.add_tool(tool)
print(len(tool_collection))  # 1
```

You can also add tools in bulk from a module, a package, or a glob pattern.

```python
tool_collection.add_tools_from_module('some_module')
tool_collection.add_tools_from_package('some_package')
tool_collection.add_tools_from_glob('*.py')
```

And here's how to use a tool:

```python
json_args = '{"name": "World"}'
result = tool_collection.use_tool("greet", json_args)
print(result)  # "Hello, World!"
```

For more detailed usage and examples, please check the API documentation and the example scripts in the `examples` folder.

## Creating New Tools

If you have an existing module that you want to work with `llmfuncs`, you can try passing it through an LLM
to generate the type hints and docstrings for any functions missing them. For example:
```
Please update this module to add type hints to all function parameters and Google style docstrings to each function.
```

## Contribute

We welcome contributions to `llmfuncs`!

## License

This project is licensed under the terms of the MIT license. For more details, see the [LICENSE](LICENSE) file.
