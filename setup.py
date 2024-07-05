from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="fin_engine",  # Required
    version="3.2",  # Required
    description="financial mining",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",
    url="https://github.com/whchien",
    author="whchien",
    author_email="locriginal@gmail.com",
    keywords="financial, python",
    # packages=find_packages(exclude=["importlib", "pymysql", "pandas"]),
)
