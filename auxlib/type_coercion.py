"""Collection of functions to coerce conversion of types with an intelligent guess."""
import collections
import re

from .compat import integer_types, string_types, iteritems, text_type
from .decorators import memoize


__all__ = ["boolify", "typify", "maybecall", "listify"]

BOOLISH = ("true", "yes", "on", "y")
BOOLABLE_TYPES = integer_types + (bool, float, complex, list, set, dict, tuple)


def _generate_regex_type_map(func=None):
    RE_BOOLEAN_TRUE = re.compile(r'^true$|^yes$|^on$', re.IGNORECASE)
    RE_BOOLEAN_FALSE = re.compile(r'^false$|^no$|^off$', re.IGNORECASE)
    RE_INTEGER = re.compile(r'^[0-9]+$')
    RE_FLOAT = re.compile(r'^[0-9]+\.[0-9]+$')
    RE_NONE = re.compile(r'^None$', re.IGNORECASE)

    REGEX_TYPE_MAP = dict({RE_BOOLEAN_TRUE: True,
                           RE_BOOLEAN_FALSE: False,
                           RE_INTEGER: int,
                           RE_FLOAT: float,
                           RE_NONE: None, })

    func.REGEX_TYPE_MAP = REGEX_TYPE_MAP
    return REGEX_TYPE_MAP


def boolify(value):
    """Convert a number, string, or sequence type into a pure boolean.

    Args:
        value (number, string, sequence): pretty much anything

    Returns:
        bool: boolean representation of the given value

    Examples:
        >>> [boolify(x) for x in ('yes', 'no')]
        [True, False]
        >>> [boolify(x) for x in (0.1, 0+0j, True, '0', '0.0', '0.1', '2')]
        [True, False, True, False, False, True, True]
        >>> [boolify(x) for x in ("true", "yes", "on", "y")]
        [True, True, True, True]
        >>> [boolify(x) for x in ("no", "non", "none", "off")]
        [False, False, False, False]
        >>> [boolify(x) for x in ([], set(), dict(), tuple())]
        [False, False, False, False]
        >>> [boolify(x) for x in ([1], set([False]), dict({'a': 1}), tuple([2]))]
        [True, True, True, True]
    """
    # cast number types naturally
    if isinstance(value, BOOLABLE_TYPES):
        return bool(value)
    # try to coerce string into number
    val = text_type(value).strip().lower().replace('.', '', 1)
    if val.isnumeric():
        return bool(float(val))
    elif val in BOOLISH:  # now look for truthy strings
        return True
    else:  # must be False
        return False


@memoize
def typify(value, type_hint=None):
    """Take a primitive value, usually a string, and try to make a more relevant type out of it.
    An optional type_hint will try to coerce the value to that type.

    Args:
        value (str, number): Usually a string, not a sequence
        type_hint (type, optional):

    Examples:
        >>> typify('32')
        32
        >>> typify('32', float)
        32.0
        >>> typify('32.0')
        32.0
        >>> typify('32.0.0')
        '32.0.0'
        >>> [typify(x) for x in ('true', 'yes', 'on')]
        [True, True, True]
        >>> [typify(x) for x in ('no', 'FALSe', 'off')]
        [False, False, False]
        >>> [typify(x) for x in ('none', 'None', None)]
        [None, None, None]

    """
    # value must be a string, or there at least needs to be a type hint
    if isinstance(value, string_types):
        value = value.strip()
    elif type_hint is None:
        # can't do anything because value isn't a string and there' no type hint
        return value

    # now we either have a stripped string, a type hint, or both
    # use the hint if it exists
    if type_hint is not None:
        return boolify(value) if type_hint == bool else type_hint(value)

    # no type hint, so try to match with the regex patterns
    for regex, typish in iteritems(getattr(typify, 'REGEX_TYPE_MAP', None)
                                   or _generate_regex_type_map(typify)):
        if regex.match(value):
            return typish(value) if callable(typish) else typish

    # nothing has caught so far; give up, and return the value that was given
    return value


def maybecall(value):
    return value() if callable(value) else value


def listify(val):
    """
    Examples:
        >>> listify('abc')
        ['abc']
        >>> listify(None)
        []
        >>> listify(False)
        [False]
        >>> listify(('a', 'b', 'c'))
        ['a', 'b', 'c']
    """
    if val is None:
        return []
    elif isinstance(val, string_types):
        return [val]
    elif isinstance(val, collections.Iterable):
        return list(val)
    else:
        return [val]
