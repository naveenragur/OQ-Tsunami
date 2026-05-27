from setuptools import setup, find_packages

setup(
    name="oq-tsunami-ext",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openquake.engine==3.25.1",
        "numpy",
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "oq-tsunami=oq_tsunami_ext.cli:main",
        ]
    },
)
