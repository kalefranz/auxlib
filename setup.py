#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(here, "auxlib")

# When executing the setup.py, we need to be able to import ourselves, this
# means that we need to add the src/ directory to the sys.path.
sys.path.insert(0, src_dir)

about = {}
with open(os.path.join(src_dir, "__about__.py")) as f:
    exec(f.read(), about)

with open(os.path.join(src_dir, ".version")) as f:
    version = f.read()


# def requirements(*f):
#     def strip_comments(l):
#         return l.split('#', 1)[0].strip()
#     return [
#         r for r in (
#             strip_comments(l) for l in open(
#                 os.path.join(os.getcwd(), 'requirements', *f)).readlines()
#         ) if r]
#

requirements = [
    "python-dateutil",
    "PyYAML",
]

test_requires = [
    "pytest",
    "pytest-cov",
    "ddt",
    "testtools",
    "radon",
    "coveralls",
    "xenon",
]


if sys.version_info < (3, 4):
    requirements.append("enum34")


setup(
    name=about["__title__"],
    version=version,

    author=about['__author__'],
    author_email=about['__email__'],
    url=about['__homepage__'],
    license=about['__license__'],

    # description=auxlib.__doc__,
    # long_description=long_description,

    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=True,

    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],

    install_requires=requirements,
    tests_require=test_requires,
)
