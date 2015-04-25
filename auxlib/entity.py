"""This module provides facilities for serializable, validatable, and type-enforcing
domain objects.

This module has many of the same motivations as the python Marshmallow package.
<http://marshmallow.readthedocs.org/en/latest/why.html>


Examples:
    >>> class Truck(Entity):
    ...     color = Field(StringType)
    ...     weight = Field(float)
    ...     wheels = Field(int, default=4, dump=False)

    >>> truck = Truck(weight=44.4, color='blue', wheels=18)
    >>> truck.wheels
    18
    >>> truck.color
    'blue'
    >>> sorted(truck.dump().items())
    [('color', 'blue'), ('weight', 44.4)]

"""
import datetime
import logging

import types
import dateutil.parser
from enum import Enum
from auxlib.exceptions import ValidationError

from auxlib.collection import AttrDict


log = logging.getLogger(__name__)


NoneType = types.NoneType
StringType = StringTypes = basestring
# IntTypes = (int, long)
NumberTypes = (int, long, float, complex)
SequenceTypes = (list, tuple, dict, set)
# TODO: NullType


# class NullType(object):
#     def __nonzero__(self):
#         return False
#
# Null = NullType()


class Field(object):
    """

    Arguments:
        types_ (primitive literal or type or sequence of types):
        default (any, optional):
        required (boolean, optional):
        validation (callable, optional):
        dump (boolean, optional):
    """

    _type = None

    def __new__(cls, *args, **kwargs):
        if cls.__name__ == 'Field':
            raise RuntimeError("The Field class should never be instantiated. "
                               "Use one of its typed subclasses.")
        return super(Field, cls).__new__(cls)

    def __init__(self, default=None, required=True, validation=None, in_dump=True):
        self._default = default
        self._required = required
        self._validation = validation
        self._in_dump = in_dump

    @property
    def name(self):
        try:
            return self._name
        except AttributeError:
            log.error("The name attribute has not been set for this field. "
                      "Call set_name at class creation time.")
            raise

    def set_name(self, name):
        self._name = name
        return self

    def __get__(self, obj, objtype):
        try:
            return obj.__dict__[self.name]
        except AttributeError:
            log.error("The name attribute has not been set for this field.")
            raise
        except KeyError:
            log.error("A value for {} has not been set".format(self.name))
            raise

    def __set__(self, obj, val):
        if not isinstance(val, self._type):
            raise TypeError("Must be a %s" % repr(self._type))
        if self._validation is not None and not self._validation(val):
            raise ValidationError(self.name, val)
        obj.__dict__[self.name] = val

    @property
    def is_required(self):
        return self._required

    @property
    def is_enum(self):
        return isinstance(self._type, type) and issubclass(self._type, Enum)

    @property
    def type(self):
        return self._type

    @property
    def default(self):
        return self._default

    @property
    def in_dump(self):
        return self._in_dump

    def __repr__(self):
        inputs = [str(self._type)]
        if not self._required:
            inputs.append("required={}".format(self._required))
        if self._default is not None:
            inputs.append("default={}".format(self._default))
        return "Field({})".format(", ".join(inputs))


class IntField(Field):
    _type = (int, long)


class StringField(Field):
    _type = basestring


class DateField(Field):
    pass




class EntityType(type):
    def __init__(cls, name, bases, attr):
        super(EntityType, cls).__init__(name, bases, attr)
        cls.__fields__ = dict(cls.__fields__) if hasattr(cls, '__fields__') else dict()
        cls.__fields__.update({name: field.set_name(name)
                               for name, field in cls.__dict__.items()
                               if isinstance(field, Field)})
        if hasattr(cls, '__register__'):
            cls.__register__()


class Entity(object):
    __metaclass__ = EntityType
    __fields__ = dict()

    def __init__(self, **kwargs):
        for key in self.__fields__:
            if key in kwargs:
                setattr(self, key, kwargs.get(key))
            else:
                field = self.__fields__.get(key)
                value = getattr(self, key, None)
                if isinstance(value, Field):
                    # value set from an inherited class, use field default
                    default = field.default() if callable(field.default) else field.default
                    if default is None:  # cannot have default of None, remove the field from the instance  # noqa
                        try:
                            # delete it if we can, otherwise just have to mask it and live with it
                            delattr(self, key)
                        except AttributeError:
                            setattr(self, key, None)
                    else:
                        setattr(self, key, default)
                elif field.is_required:
                    # now safe to use value, with validation
                    setattr(self, key, value)
        self.validate()

    @classmethod
    def create_from_objects(cls, *objects, **override_fields):
        init_vars = dict()
        search_maps = (AttrDict(override_fields), ) + objects
        for key, field in cls.__fields__.iteritems():
            value = find_or_none(key, search_maps)
            if value is not None or field.is_required:
                init_vars[key] = field.type(value) if field.is_enum else value
        return cls(**init_vars)

    @classmethod
    def load(cls, data_dict):
        return cls(**data_dict)

    def validate(self):
        (getattr(self, name) for name, field in self.__fields__.items() if field.is_required)

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join("{}={}".format(key, repr(value)) for key, value in self.__dict__.items()))

    @classmethod
    def __register__(cls):
        pass

    def dump(self):
        d = self.__dict__
        convert = lambda v: (v.isoformat() if hasattr(v, 'isoformat')
                             else v.value if hasattr(v, 'value')
                             else v )
        return {field.name: value
                for field, value in ((field, convert(d[field.name]))  # run conversion on values
                                     for field in self.__dump_fields())
                if value is not None or field.is_required}  # filter out final values

    @classmethod
    def __dump_fields(cls):
        if '__dump_fields_cache' not in cls.__dict__:
            cls.__dump_fields_cache = set([field for field in cls.__fields__.itervalues()
                                       if field.dump])
        return cls.__dump_fields_cache

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return all(getattr(self, field) == getattr(other, field) for field in self.__fields__)

    def __hash__(self):
        return sum(hash(getattr(self, field)) for field in self.__fields__)


def find_or_none(key, search_maps):
    """Return the value of the first key found in the list of search_maps,
    otherwise return None.

    Examples:
        >>> d1 = AttrDict({'a': 1, 'b': 2, 'c': 3, 'e': None})
        >>> d2 = AttrDict({'b': 5, 'e': 6, 'f': 7})
        >>> find_or_none('c', (d1, d2))
        3
        >>> find_or_none('f', (d1, d2))
        7
        >>> find_or_none('b', (d1, d2))
        2
        >>> print find_or_none('g', (d1, d2))
        None
        >>> find_or_none('e', (d1, d2))
        6

    """
    try:
        for d in search_maps:
            return (getattr(d, key) if getattr(d, key) is not None
                    else find_or_none(key, search_maps[1:]))
        else:
            return None
    except AttributeError:
        return find_or_none(key, search_maps[1:])
