# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Extension package for GEM OpenQuake Engine.
#
# This repository is intentionally plugin-only: it does NOT vendor the
# OpenQuake engine source code. Install oq-engine (v3.25.1 recommended)
# separately (pip or editable source checkout), then install this package.

import pathlib

from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).resolve().parent


def read_readme():
    p = HERE / "README.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


setup(
    name="oq-tsunami-ext",
    version="0.1.0",
    description="OQ-Tsunami patch tool for native OpenQuake tsunami risk workflows",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=[
        "matplotlib",
        "numpy",
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "oq-tsunami=oq_tsunami_ext.cli:main",
        ]
    },
    python_requires=">=3.9",
    zip_safe=False,
)
