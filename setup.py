#!/usr/bin/env python3
import pathlib
import sys
import typing
from glob import glob
from os.path import basename, dirname, splitext

from setuptools import find_namespace_packages, setup  # type: ignore

PROJECT_NAME: str = ""
PYTHON_VERSION: tuple[int] = (3, 10)

if sys.version_info < PYTHON_VERSION:
    raise RuntimeError(f"{PROJECT_NAME} requires Python {'.'.join([str(x) for x in PYTHON_VERSION])}+")

HERE = pathlib.Path(__file__).parent
IS_GIT_REPO: bool = (HERE / ".git").exists()

base_dir: str = dirname(__file__)

__pkginfo__: typing.Dict[str, typing.Any] = {}
exec(
    (HERE / "__pkginfo__.py").read_text("utf-8"), __pkginfo__
)  # pylint: disable=exec-used

version: str = str(__pkginfo__.get("version", ""))

long_description: str = (HERE / "README.md").read_text("utf-8").strip()

setup(
    author="Steve Cirelli",
    author_email="scirelli@gmail.com",
    maintainer=", ".join(""),
    name=PROJECT_NAME,
    version=version,
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_namespace_packages("src"),
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    package_data={"<main package name>": ["py.typed"]},
    include_package_data=True,
    test_suite="tests.unit",
    dependency_links=[],
    install_requires=[
    ],
    setup_requires=["pytest-runner", "behave"],
    python_requires=f">={'.'.join([str(x) for x in PYTHON_VERSION])}",
    zip_safe=False,
    keywords="",
    license="MIT",
    classifiers=[
        "Development Status :: 1 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        f"Programming Language :: Python :: {PYTHON_VERSION[0]}",
    ],
)
