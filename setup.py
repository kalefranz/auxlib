#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import auxlib.version

name = "auxlib"
long_description = """
"""


setup(
    name=name,
    author='Kale Franz',
    author_email='kale@franz.io',
    description="auxiliary library to the python standard library",
    license='ISC',
    long_description=long_description,
    packages=find_packages(),
    url='https://github.com/kalefranz/auxlib',
    version=auxlib.version.get_version(),
    zip_safe=True,

    install_requires=[
    ],

    setup_requires=[
        'wheel',
    ],

    tests_require=[
    ],
)
