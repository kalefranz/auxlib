# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

try:
    from collections import OrderedDict as odict
except ImportError:
    from ordereddict import OrderedDict as odict

from ._vendor.five import with_metaclass  # NOQA
from ._vendor.six import (string_types, text_type, integer_types, iteritems, itervalues,
                          iterkeys, wraps)  # NOQA
