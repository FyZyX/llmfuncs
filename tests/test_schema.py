import types
import unittest
from typing import List, Optional

from llmfuncs.schema import from_module

import example


def test_function1(x: int, y: str = "hello") -> str:
    """This is a test function.

    Args:
        x (int): An integer.
        y (str, optional): A string. Defaults to "hello".

    Returns:
        str: A string.
    """
    return y * x


def test_function2(a: float, b: Optional[List[int]] = None) -> List[int]:
    """This is another test function.

    Args:
        a (float): A float.
        b (Optional[List[int]], optional): A list of integers. Defaults to None.

    Returns:
        List[int]: A list of integers.
    """
    return [int(a)] * (len(b) if b else 1)


# Creating a dummy module
dummy_module = types.ModuleType("dummy_module")
dummy_module.test_function1 = test_function1
dummy_module.test_function2 = test_function2


class TestSchemaExtraction(unittest.TestCase):
    def test_schema_from_module(self):
        schema = from_module(dummy_module)
        self.assertEqual(len(schema), 2)

        schema_dict = {s["name"]: s for s in schema}

        self.assertIn("test_function1", schema_dict)
        self.assertIn("test_function2", schema_dict)

        schema1 = schema_dict["test_function1"]
        self.assertEqual(schema1["description"], "This is a test function.")
        self.assertIn("parameters", schema1)
        self.assertIn("x", schema1["parameters"]["properties"])
        self.assertEqual(schema1["parameters"]["properties"]["x"]["type"], "integer")

        schema2 = schema_dict["test_function2"]
        self.assertEqual(schema2["description"], "This is another test function.")
        self.assertIn("parameters", schema2)
        self.assertIn("a", schema2["parameters"]["properties"])
        self.assertEqual(schema2["parameters"]["properties"]["a"]["type"], "number")

    def test_schema_from_module_example(self):
        actual_schema = from_module(example)
        expected_schema = [
            {
                "name": "append_file",
                "description": "Appends content to a file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The name of the file to append to.",
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to append to the file.",
                        },
                    },
                    "required": ["filename", "content"],
                },
            },
            {
                "name": "ask_clarification",
                "description": "Ask the user a clarifying question about the project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The question to ask the user.",
                        },
                    },
                    "required": ["question"],
                },
            },
            {
                "name": "create_dir",
                "description": "Create a directory with given name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "The name of the directory to create.",
                        },
                    },
                    "required": ["directory"],
                },
            },
            {
                "name": "delete_file",
                "description": "Deletes a file with given name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The name of the file to delete.",
                        },
                    },
                    "required": ["filename"],
                },
            },
            {
                "name": "list_files",
                "description": "List the files in the current project.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "project_finished",
                "description": "Call this function when the project is finished.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "read_file",
                "description": "Read the contents of a file with given name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The name of the file to read from.",
                        },
                    },
                    "required": ["filename"],
                },
            },
            {
                "name": "write_file",
                "description": "Writes content to a file with given name. "
                               "Existing files will be overwritten.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The name of the file to write to.",
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file.",
                        },
                    },
                    "required": ["filename", "content"],
                },
            },
        ]
        self.assertListEqual(actual_schema, expected_schema)


if __name__ == '__main__':
    unittest.main()
