# -*- coding: utf-8 -*-
"""Common collection classes."""
from __future__ import print_function, division, absolute_import

from .ish import attribute_or_item

from collections import OrderedDict

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
    # TODO: enforce keys are strings









class KeyedList(list):
    """
    requirements:
      - openssl
      - readline
      - tk
      - zlib

    """





class DictList(list):
    """
    Examples:
        >> people = DictList({'name': 'Bob', 'state': 'CO'}, {'name': 'Jane', 'state': 'TX'})
        >> people[0]
        {'name': 'Bob', 'state': 'CO'}
        >> people.Jane
        {'name': 'Jane', 'state': 'TX'}
        >> people['Bob']['state']
        'CO'

        >> dogs = DictList('Darwin': {'color': 'black'}, 'Turtle': {'color': 'golden'})
        >> dogs.Darwin['color']
        'black'
        >> dogs[1]
        {'color': 'golden'}
        >> dogs[1].name
        'Turtle'
        >> dogs['Turtle']['color']
        'golden'

        >> sheep = DictList('Nitro': 2000, 'Jefferson': 1998)
        >> sheep[0]
        2000
        >> sheep[0].name
        'Nitro'
        >> sheep.Jefferson, sheep['Jefferson']
        1998, 1998
    """
    def __init__(self, iterable=tuple()):
        super(DictList, self).__init__(iterable)
        try:
            name_map = {attribute_or_item(obj, 'name'): q for q, obj in enumerate(self)}
        except KeyError:
            pass  # each element must have a 'name' field

    def __getattr__(self, item):
        name_map = {attribute_or_item(obj, 'name'): q for q, obj in enumerate(self)}


class OverwriteFailDict(dict):

    def __setitem__(self, key, value):
        if key in self:
            raise KeyError("The key '{0}' is already set.\n"
                           "Refusing to overwrite {1} with {2}".format(key, self[key], value))
        super(OverwriteFailDict, self).__setitem__(key, value)


class OD(OrderedDict):

    # def __new__(cls, iterable=tuple()):
    #     # if iterable is map type, none of the elements should have a 'name' field and all keys should be strings
    #     # if iterable is not a map type, each element must have a 'name' field and the value must be a string
    #
    #     obj = super(OrderedDict, cls).__new__(cls, *args, **kwargs)
    #     obj._from_base_class = type(obj) == OrderedDict
    #     return obj

    def __init__(self, iterable=None, **kwargs):
        super(OD, self).__init__(iterable, **kwargs)
        self.__name_map = OverwriteFailDict((attribute_or_item(obj, 'name'), q)
                                            for q, obj in enumerate(self))


    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        super(OD, self).__setitem__(key, value)

    def __getitem__(self, item):
        if isinstance(item, int):



def instantiate(cls, *args, **kwargs):
    obj = cls.__new__(cls, *args, **kwargs)
    if isinstance(obj,cls):
        cls.__init__(obj, *args, **kwargs)
    return obj