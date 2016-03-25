# -*- coding: utf-8 -*-
"""Auxlib is an auxiliary library to the python standard library.

The aim is to provide core generic features for app development in python. Auxlib fills in some
python stdlib gaps much like `pytoolz <https://github.com/pytoolz/>`_ has for functional
programming, `pyrsistent <https://github.com/tobgu/pyrsistent/>`_ has for data structures, or
`boltons <https://github.com/mahmoud/boltons/>`_ has generally.

Major areas addressed are:
  - package versioning, with a clean and less invasive alternative to
    versioneer (auxlib.packaging)
  - a map implementation designed specifically to hold application configuration and context
    information (auxlib.configuration)
  - intelligent type coercion utilities (:ref:`type_coercion`)
  - factory pattern (auxlib.factory)
  - robust base class for type-enforced data models and transfer objects (auxlib.entity)
  - file path utilities especially helpful when working with various python package
    formats (auxlib.path)
  - logging initialization routines to simplify python logging setup (auxlib.logz)
  - simple, but correct, pycrypto wrapper (auxlib.crypt)


"""
from __future__ import absolute_import, division, print_function
from logging import getLogger, NullHandler

# don't mess up logging for users
getLogger('auxlib').addHandler(NullHandler())

from .packaging import BuildPyCommand, SDistCommand, Tox, get_version  # NOQA

__all__ = [
    "__name__", "__version__", "__author__",
    "__email__", "__license__", "__copyright__",
    "__summary__", "__url__",
    "BuildPyCommand", "SDistCommand", "Tox", "get_version",
]

__version__ = get_version(__file__, __package__)

__name__ = "auxlib"
__author__ = 'Kale Franz'
__email__ = 'kale@franz.io'
__url__ = 'https://github.com/kalefranz/auxlib'
__license__ = "ISC"
__copyright__ = "(c) 2015 Kale Franz. All rights reserved."
__summary__ = """auxiliary library to the python standard library"""
