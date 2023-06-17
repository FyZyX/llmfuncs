from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llmfuncs",
    version="0.1.1",
    url="https://github.com/FyZyX/llmfuncs",
    author="Lucas Lofaro",
    author_email="lucasmlofaro@gmail.com",
    description="Dynamically generate JSON Schema from Python code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        "docstring-parser~=0.15",
    ],
)
