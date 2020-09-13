#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages
from distutils.spawn import find_executable


def get_exec_name():
    """Handles the case for when the user already has the official in3 CLI installed.
    Will then install as in3alt.
    """
    # TODO: Detect that it is the official in3 somehow
    if find_executable("in3"):
        return "in3alt"
    return "in3"


setup(
    name="in3cli",
    version="0.1.0",
    description="A CLI for the Incubed protocol",
    author="Juliya Smith",
    author_email="juliya@juliyasmith.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">3, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4",
    install_requires=["click>=7.1.1", "in3>=1.0.0", "keyring>=21.4.0"],
    extras_require={
        "dev": [
            "flake8==3.8.3",
            "pytest==4.6.11",
            "pytest-cov==2.10.0",
            "pytest-mock==2.0.0",
            "tox>=3.17.1",
        ]
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    entry_points={"console_scripts": ["{}=in3cli.main:cli".format(get_exec_name())]},
)
