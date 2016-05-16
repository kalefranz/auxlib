# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import os
from setuptools import setup, find_packages
import sys

# When executing the setup.py, we need to be able to import ourselves, this
# means that we need to add the src directory to the sys.path.
here = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(here, "auxlib")
sys.path.insert(0, src_dir)
import auxlib  # NOQA

requirements = []

if sys.version_info < (3, 4):
    requirements.append("enum34")

if sys.version_info < (2, 7):
    requirements.append("ordereddict")

with open(os.path.join(here, "README.rst")) as f:
    long_description = f.read()

setup(
    name=auxlib.__name__,
    version=auxlib.__version__,

    author=auxlib.__author__,
    author_email=auxlib.__email__,
    url=auxlib.__url__,
    license=auxlib.__license__,

    description=auxlib.__summary__,
    long_description=long_description,

    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,

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
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],

    install_requires=requirements,
    tests_require=["tox"],
    extras_require={
        'crypt': ["pycrypto"],
        'yaml': ["pyyaml"],
    },
    cmdclass={
        'build_py': auxlib.BuildPyCommand,
        'sdist': auxlib.SDistCommand,
        'test': auxlib.Tox,
    },
)
