from setuptools import setup, find_packages

setup(
    name="llmfuncs",
    version="0.1.0",
    url="https://github.com/FyZyX/llmfuncs",
    author="Lucas Lofaro",
    author_email="lucasmlofaro@gmail.com",
    description="Dynamically generate JSON Schema from Python code.",
    packages=find_packages(),
    install_requires=[
        "docstring-parser~=0.15",
    ],
)
