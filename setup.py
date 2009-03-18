#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='Hugh',
    version='0.1',
    packages=find_packages(),
    install_requires = [
        'Werkzeug',
    ],
)
