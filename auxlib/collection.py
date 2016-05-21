# -*- coding: utf-8 -*-
"""Common collection classes."""
from __future__ import print_function, division, absolute_import


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


def first(seq, key=lambda x: bool(x), default=None, apply=lambda x: x):
    """Give the first value that satisfies the key test.

    Args:
        seq (iterable):
        key (callable): test for each element of iterable
        default: returned when all elements fail test
        apply (callable): applied to element before return

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
    return next((apply(x) for x in seq if key(x)), default)


def cumulative_first(seq, key=lambda x: bool(x), apply=lambda x: x):
    """like first, but cumulative, up to and including first

    unlike first, there is no default; where default would be returned in first, all of seq is
    returned in cumulative_first

    Args:
        seq (iterable):
        key (callable): test for each element of seq
        apply (callable): applied to each element before return

    Examples:
        >>> cumulative_first([0, False, None, [], (), 42])
        (0, False, None, [], (), 42)
        >>> cumulative_first([0, False, 'some', [], (), 42])
        (0, False, 'some')

    """
    lst = []
    for element in seq:
        lst.append(apply(element))
        if key(element):
            break
    return tuple(lst)


def last(seq, key=lambda x: bool(x), default=None, apply=lambda x: x):
    return next((apply(x) for x in reversed(seq) if key(x)), default)

