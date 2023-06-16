# llmfuncs

`llmfuncs` is a Python package that programmatically extracts function definitions and converts them to a JSON schema format that can be used with OpenAI's language models.

## Installation

You can install the package via pip:

```bash
pip install llmfuncs
```

## Usage

Import the main function `schema_from_module` from `llmfuncs` and pass in a module:

```python
from llmfuncs import schema
import your_module

schema = schema.from_module(your_module)
```

> **NOTE:** If your function parameters don't have type hints, they will be ignored!

The returned `schema` will be a list of JSON schema representations of the functions in the given module.

## Creating New Tools

If you have an existing module that you want to work with `llmfuncs`, you can try passing it through an LLM
to generate the type hints and docstrings for any functions missing them. For example:
```
Please update this module to add type hints to all function parameters and Google style docstrings to each function.
```


## Features

- Extracts function name, description (from docstring), parameters, and their types
- Includes default values for parameters in the description
- Supports functions with arguments that have type hints
- Converts Python types to corresponding JSON schema types

## Contributing

To contribute to `llmfuncs`, fork the repository and submit a Pull Request!

## License

MIT