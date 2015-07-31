#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import os
import re
import sys

import auxlib
from auxlib import packaging

name = "auxlib"
long_description = """
"""

here = os.path.abspath(os.path.dirname(__file__))
PY3 = sys.version_info[0] == 3
re_meta = re.compile(r'__(\w+?)__\s*=\s*(.*)')
rq = lambda s: s.strip("\"'")


with open(os.path.join(here, '{}/__init__.py'.format(name))) as meta_fh:
    meta = {}

    def add_default(m):
        attr_name, attr_value = m.groups()
        return ((attr_name, rq(attr_value)), )

    for line in meta_fh:
        if line.strip() == '# -eof meta-':
            break
        m = re_meta.match(line.strip())
        if m:
            meta.update(add_default(m))


setup(
    name=name,
    author=meta['author'],
    author_email=meta['contact'],
    description=auxlib.__doc__,
    license=meta['license'],
    long_description=long_description,
    packages=find_packages(exclude=['tests', 'tests.*']),
    url=meta['homepage'],
    version=auxlib.__version__,
    include_package_data = True,
    zip_safe=True,
    install_requires=packaging.requirements('default.txt'),
    setup_requires=packaging.requirements('setup.txt'),
    tests_require=packaging.requirements('test.txt'),
)
