# -*- coding: utf-8 -*-
"""Common collection classes."""
from __future__ import print_function, division, absolute_import
from functools import reduce
from collections import Mapping, Set

from .compat import isiterable, iteritems, odict, text_type


def make_immutable(value):
    # this function is recursive, and if nested data structures fold back on themselves,
    #   there will likely be recursion errors
    if isinstance(value, Mapping):
        if isinstance(value, frozenodict):
            return value
        return frozenodict((k, make_immutable(v)) for k, v in iteritems(value))
    elif isinstance(value, Set):
        if isinstance(value, frozenset):
            return value
        return frozenset(make_immutable(v) for v in value)
    elif isiterable(value):
        if isinstance(value, tuple):
            return value
        return tuple(make_immutable(v) for v in value)
    else:
        return value


# http://stackoverflow.com/a/14620633/2127762
class AttrDict(dict):
    """Sub-classes dict, and further allows attribute-like access to dictionary items.

    Examples:
        >>> d = AttrDict({'a': 1})
        >>> d.a, d['a'], d.get('a')
        (1, 1, 1)
        >>> d.b = 2
        >>> d.b, d['b']
        (2, 2)
    """
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class frozendict(Mapping):
    dict_cls = dict

    def __init__(self, *args, **kwargs):
        self._dict = self.dict_cls(*args, **kwargs)
        self._hash = None

    def __getitem__(self, key):
        return self._dict[key]

    def __contains__(self, key):
        return key in self._dict

    def copy(self, **add_or_replace):
        return self.__class__(self, **add_or_replace)

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self._dict)

    def __hash__(self):
        if self._hash is None:
            h = 0
            for key, value in iteritems(self._dict):
                h ^= hash((key, value))
            self._hash = h
        return self._hash

    def __json__(self):
        return self._dict


class frozenodict(frozendict):
    dict_cls = odict


def first(seq, key=lambda x: bool(x), default=None, apply=lambda x: x):
    """Give the first value that satisfies the key test.

    Args:
        seq (iterable):
        key (callable): test for each element of iterable
        default: returned when all elements fail test
        apply (callable): applied to element before return, but not to default value

    Returns: first element in seq that passes key, mutated with optional apply

    Examples:
        >>> first([0, False, None, [], (), 42])
        42
        >>> first([0, False, None, [], ()]) is None
        True
        >>> first([0, False, None, [], ()], default='ohai')
        'ohai'
        >>> import re
        >>> m = first(re.match(regex, 'abc') for regex in ['b.*', 'a(.*)'])
        >>> m.group(1)
        'bc'

        The optional `key` argument specifies a one-argument predicate function
        like that used for `filter()`.  The `key` argument, if supplied, must be
        in keyword form.  For example:
        >>> first([1, 1, 3, 4, 5], key=lambda x: x % 2 == 0)
        4

    """
    return next((apply(x) for x in seq if key(x)), default() if callable(default) else default)


def firstitem(map, key=lambda k, v: bool(k), default=None, apply=lambda k, v: (k, v)):
    return next((apply(k, v) for k, v in map if key(k, v)), default)


def last(seq, key=lambda x: bool(x), default=None, apply=lambda x: x):
    return next((apply(x) for x in reversed(seq) if key(x)), default)


def call_each(seq):
    """Calls each element of sequence to invoke the side effect.

    Args:
        seq:

    Returns: None

    """
    try:
        reduce(lambda _, y: y(), seq)
    except TypeError as e:
        if text_type(e) != "reduce() of empty sequence with no initial value":
            raise
