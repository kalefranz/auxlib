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

from auxlib.exceptions import ValidationError, Raise
from auxlib.collection import AttrDict


log = logging.getLogger(__name__)

KEY_OVERRIDES_MAP = "__key_overrides__"


class Field(object):
    """

    Arguments:
        types_ (primitive literal or type or sequence of types):
        default (any, callable, optional):
        required (boolean, optional):
        validation (callable, optional):
        dump (boolean, optional):
    """

    def __init__(self, default=None, required=True, validation=None, in_dump=True, nullable=False):
        self._default = default
        self._required = required
        self._validation = validation
        self._in_dump = in_dump
        self._nullable = nullable
        if default is not None:
            self.validate(default)

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
        if obj is None:
            # handle the case of fields inherited from subclass but overrode on class object
            return getattr(objtype, KEY_OVERRIDES_MAP)[self.name]
        try:
            val = obj.__dict__[self.name]
            return val() if callable(val) else val
        except AttributeError as e:
            log.error("The name attribute has not been set for this field.")
            raise
        except KeyError:
            if self.default is not None:
                val = self.default
                return val() if callable(val) else val
            elif self._nullable:
                return None
            else:
                raise AttributeError("A value for {} has not been set".format(self.name))

    def __set__(self, obj, val):
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
        val = val() if callable(val) else val
        if not isinstance(val, self._type):
            if val is None and not self.required:
                return False
            else:
                raise ValidationError(getattr(self, 'name', 'undefined name'), val, self._type)
        elif self._validation is not None and not self._validation(val):
            raise ValidationError(getattr(self, 'name', 'undefined name'), val)
        else:
            return True


    @property
    def required(self):
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

    @property
    def nullable(self):
        return self._nullable


class IntField(Field):
    _type = (int, long)


class StringField(Field):
    _type = basestring


class NumberField(Field):
    _type = (int, long, float, complex)


class DateField(Field):
    _type = datetime.datetime

    def __init__(self, default=None, required=True, validation=None, in_dump=True):
        super(DateField, self).__init__(self._pre_convert(default), required, validation, in_dump)

    def __get__(self, obj, objtype):
        return super(DateField, self).__get__(obj, objtype).isoformat()

    def __set__(self, obj, val):
        try:
            super(DateField, self).__set__(obj, self._pre_convert(val))
        except (ValueError, AttributeError):
            raise ValidationError(self.name, val, self._type)

    def _pre_convert(self, val):
        return dateutil.parser.parse(val) if isinstance(val, basestring) else val


class EnumField(Field):

    def __init__(self, enum_class, default=None, required=True, validation=None, in_dump=True):
        self._type = enum_class
        super(EnumField, self).__init__(self._pre_convert(default), required, validation, in_dump)

    def __get__(self, obj, objtype):
        return super(EnumField, self).__get__(obj, objtype).value

    def __set__(self, obj, val):
        try:
            super(EnumField, self).__set__(obj, self._pre_convert(val))
        except ValueError:
            raise ValidationError(self.name, val, self._type)

    def _pre_convert(self, val):
        return self._type(val) if val is not None and not isinstance(val, self._type) else val


class ListField(Field):
    _type = tuple

    def __init__(self, element_type, default=None, required=True, validation=None, in_dump=True):
        self._element_type = element_type
        super(ListField, self).__init__(self._pre_convert(default), required, validation, in_dump)

    def __set__(self, obj, val):
        super(ListField, self).__set__(obj, self._pre_convert(val))

    def _pre_convert(self, val):
        if val is None:
            return None
        else:
            et = self._element_type
            return tuple(el if isinstance(el, et)
                         else Raise(ValidationError(self.name, el, et))
                         for el in val)


class EntityType(type):

    def __new__(mcs, name, bases, dct):
        # if we're about to mask a field that's already been created with something that's
        #  not a field, then assign it to an alternate variable name
        non_field_keys = (key for key, value in dct.iteritems()
                          if not isinstance(value, Field) and not key.startswith('__'))
        try:
            entity_subclasses = [base for base in bases
                                 if issubclass(base, Entity) and base is not Entity]
        except NameError:
            # NameError: global name 'Entity' is not defined
            entity_subclasses = []
        if entity_subclasses:
            keys_to_override = [key for key in non_field_keys
                                if any(isinstance(base.__dict__.get(key, None), Field)
                                       for base in entity_subclasses)]
            dct[KEY_OVERRIDES_MAP] = {key: dct.pop(key) for key in keys_to_override}

        return super(EntityType, mcs).__new__(mcs, name, bases, dct)

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
    # TODO: add arg order to fields like in enum34

    def __init__(self, **kwargs):
        for key, field in self.__fields__.iteritems():
            try:
                setattr(self, key, kwargs[key])
            except KeyError:
                # handle the case of fields inherited from subclass but overrode on class object
                if key in getattr(self, KEY_OVERRIDES_MAP, []):
                    setattr(self, key, getattr(self, KEY_OVERRIDES_MAP)[key])
        self.validate()

    @classmethod
    def create_from_objects(cls, *objects, **override_fields):
        init_vars = dict()
        search_maps = (AttrDict(override_fields), ) + objects
        for key, field in cls.__fields__.iteritems():
            value = find_or_none(key, search_maps)
            if value is not None or field.required:
                init_vars[key] = field.type(value) if field.is_enum else value
        return cls(**init_vars)

    @classmethod
    def load(cls, data_dict):
        return cls(**data_dict)

    def validate(self):
        try:
            reduce(lambda x, y: y, (getattr(self, name)
                                    for name, field in self.__fields__.items()
                                    if field.required))
        except AttributeError as e:
            raise ValidationError(None, msg=e.message)
        except TypeError as e:
            if "no initial value" not in e.message:
                raise

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
                for field, value in ((field, getattr(self, field.name, None))
                                     for field in self.__dump_fields())
                if value is not None or field.nullable}

    @classmethod
    def __dump_fields(cls):
        if '__dump_fields_cache' not in cls.__dict__:
            cls.__dump_fields_cache = set([field for field in cls.__fields__.itervalues()
                                           if field.in_dump])
        return cls.__dump_fields_cache

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        rando_default = 192837465647382910
        return all(getattr(self, field, rando_default) == getattr(other, field, rando_default)
                   for field in self.__fields__)

    def __hash__(self):
        return sum(hash(getattr(self, field, None)) for field in self.__fields__)


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
