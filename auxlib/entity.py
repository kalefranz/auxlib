"""This module provides facilities for serializable, validatable, and type-enforcing
domain objects.

This module has many of the same motivations as the python Marshmallow package.
<http://marshmallow.readthedocs.org/en/latest/why.html>


Examples:
    >>> class Color(Enum):
    ...     blue = 0
    ...     black = 1
    ...     red = 2
    >>> class Truck(Entity):
    ...     color = EnumField(Color)
    ...     weight = NumberField()
    ...     wheels = IntField(4, in_dump=False)

    >>> truck = Truck(weight=44.4, color=Color.blue, wheels=18)
    >>> truck.wheels
    18
    >>> truck.color
    0
    >>> sorted(truck.dump().items())
    [('color', 0), ('weight', 44.4)]

"""
import datetime
import logging

import dateutil.parser
from enum import Enum
from auxlib.exceptions import ValidationError

from auxlib.collection import AttrDict


log = logging.getLogger(__name__)


class Field(object):
    """

    Arguments:
        types_ (primitive literal or type or sequence of types):
        default (any, callable, optional):
        required (boolean, optional):
        validation (callable, optional):
        dump (boolean, optional):
    """

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
            if self.default is not None:
                return self.default
            else:
                raise AttributeError("A value for {} has not been set".format(self.name))

    def __set__(self, obj, val):
        if callable(val):
            val = val()
        # validate will raise an exception if invalid
        # validate will return False if the value should be removed
        if self.validate(val):
            obj.__dict__[self.name] = val
        else:
            obj.__dict__.pop(self.name, None)

    def validate(self, val):
        """

        Returns:
            True: if val is valid
            False: if val should be unset for the field

        Raises:
            ValidationError
        """
        if not isinstance(val, self._type):
            if val is None and not self.is_required:
                return False
            else:
                raise ValidationError(self.name, val, self._type)
        elif self._validation is not None and not self._validation(val):
            raise ValidationError(self.name, val)
        else:
            return True


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
        return self._default() if callable(self._default) else self._default

    @property
    def in_dump(self):
        return self._in_dump

    def __repr__(self):
        inputs = [str(self._type)]
        if not self._required:
            inputs.append("required={}".format(self._required))
        if self._default is not None:
            inputs.append("default={}".format(self._default))
        return "{}({})".format(self.__class__.__name__, ", ".join(inputs))


class IntField(Field):
    _type = (int, long)


class StringField(Field):
    _type = basestring


class NumberField(Field):
    _type = (int, long, float, complex)


class DateField(Field):
    _type = datetime.datetime

    def __get__(self, obj, objtype):
        return super(DateField, self).__get__(obj, objtype).isoformat()

    def __set__(self, obj, val):
        try:
            val = val() if callable(val) else val
            value = val if isinstance(val, datetime.datetime) else dateutil.parser.parse(val)
            super(DateField, self).__set__(obj, value)
        except (ValueError, AttributeError):
            raise ValidationError(self.name, val, self._type)


class EnumField(Field):

    def __init__(self, enum_class, *args, **kwargs):
        self._type = enum_class
        super(EnumField, self).__init__(*args, **kwargs)

    def __get__(self, obj, objtype):
        return super(EnumField, self).__get__(obj, objtype).value

    def __set__(self, obj, val):
        try:
            value = val if isinstance(val, self._type) else self._type(val)
            super(EnumField, self).__set__(obj, value)
        except ValueError:
            raise ValidationError(self.name, val, self._type)



class EntityType(type):

    def __init__(cls, name, bases, attr):
        super(EntityType, cls).__init__(name, bases, attr)
        cls.__fields__ = dict(cls.__fields__) if hasattr(cls, '__fields__') else dict()
        cls.__fields__.update({name: field.set_name(name)
                               for name, field in cls.__dict__.items()
                               if isinstance(field, Field)})
        cls.__validate_defaults()
        if hasattr(cls, '__register__'):
            cls.__register__()

    def __validate_defaults(cls):
        (field.validate(field.default)
         for field in cls.__fields__.values()
         if field.default is not None)


class Entity(object):
    __metaclass__ = EntityType
    __fields__ = dict()
    # TODO: add arg order to fields like in enum34

    def __init__(self, **kwargs):
        for key in self.__fields__:
            if key in kwargs:
                setattr(self, key, kwargs.get(key))
            else:
                field = self.__fields__.get(key)
                if field.is_required:
                    setattr(self, key, field.default)
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
        _repr = lambda val: repr(val.value) if isinstance(val, Enum) else repr(val)
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join("{}={}".format(key, _repr(value)) for key, value in self.__dict__.items()))

    @classmethod
    def __register__(cls):
        pass

    def dump(self):
        return {field.name: value
                for field, value in ((field, getattr(self, field.name))
                                     for field in self.__dump_fields()
                                     if field.is_required)
                if value is not None}

    @classmethod
    def __dump_fields(cls):
        if '__dump_fields_cache' not in cls.__dict__:
            cls.__dump_fields_cache = set([field for field in cls.__fields__.itervalues()
                                           if field.in_dump])
        return cls.__dump_fields_cache

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return all(getattr(self, field) == getattr(other, field) for field in self.__fields__)

    def __hash__(self):
        return sum(hash(getattr(self, field)) for field in self.__fields__)


def find_or_none(key, search_maps, map_index=0):
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
        attr = getattr(search_maps[map_index], key)
        return attr if attr is not None else find_or_none(key, search_maps[1:])
    except AttributeError:
        # not found in first map object, so go to next
        return find_or_none(key, search_maps, map_index+1)
    except IndexError:
        # ran out of map objects to search
        return None
