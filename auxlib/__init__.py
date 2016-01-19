# -*- coding: utf-8 -*-
"""auxiliary library to the python standard library"""
from __future__ import absolute_import, division, print_function
import os
import sys
import warnings

from auxlib.__about__ import (
    __author__, __copyright__, __email__, __license__, __summary__, __title__,
    __homepage__
)

__all__ = [
    "__title__", "__version__", "__author__",
    "__email__", "__license__", "__copyright__",
    "__homepage__",
]

vfile = os.path.join(os.path.dirname(__file__), '.version')
with open(vfile, 'r') as f:
    __version__ = f.read().strip()
