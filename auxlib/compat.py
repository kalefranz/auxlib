# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from itertools import chain

try:
    from collections import OrderedDict as odict
except ImportError:
    from ordereddict import OrderedDict as odict

from ._vendor.five import with_metaclass, WhateverIO as StringIO  # NOQA
from ._vendor.six import (string_types, text_type, integer_types, iteritems, itervalues,
                          iterkeys, wraps)  # NOQA

NoneType = type(None)
primitive_types = tuple(chain(string_types, integer_types, (float, complex, bool, NoneType)))
