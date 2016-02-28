# -*- coding: utf-8 -*-
"""auxiliary library to the python standard library"""
from __future__ import absolute_import, division, print_function

from .packaging import BuildPyCommand, SdistCommand, Tox, get_version

__all__ = [
    "__title__", "__version__", "__author__",
    "__email__", "__license__", "__copyright__",
    "__summary__", "__homepage__",
    "BuildPyCommand", "SdistCommand", "Tox", "get_version",
]

__version__ = get_version(__file__, __package__)

__title__ = "auxlib"
__author__ = 'Kale Franz'
__email__ = 'kale@franz.io'
__homepage__ = 'https://github.com/kalefranz/auxlib'
__license__ = "ISC"
__copyright__ = "(c) 2015 Kale Franz. All rights reserved."
__summary__ = __doc__
