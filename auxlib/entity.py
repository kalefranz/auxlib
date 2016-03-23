# -*- coding: utf-8 -*-
"""This module provides facilities for serializable, validatable, and type-enforcing
domain objects.

This module has many of the same motivations as the python Marshmallow package.
<http://marshmallow.readthedocs.org/en/latest/why.html>

Also need to be explicit in explaining what Marshmallow doesn't do, and why this module is needed.
  - Provides type safety like an ORM. And like an ORM, all classes subclass Entity.
  - Provides BUILT IN serialization and deserialization.  Marhmallow requires a lot of code
    duplication.

This module gives us:
  - type safety
  - custom field validation
  - serialization and deserialization
  - rock solid foundational domain objects


Comparison to schematics:
  - no get_mock_object method (yet)
  - no context-dependent serialization or MultilingualStringType
  - name = StringType(serialized_name='person_name')
  - name = StringType(serialize_when_none=False)
  - more flexible validation error messages


TODO:
  - alternate field names
  - add dump_if_null field option
  - consider adding immutability, maybe ImmutableEntity


Optional Field Properties:
  - validation = None
  - default = None
  - required = True
  - in_dump = True
  - nullable = False

Behaviors:
  - Nullable is a "hard" setting, in that the value is either always or never allowed to be None.
  - What happens then if required=False and nullable=False?
      - The object can be init'd without a value (though not with a None value).
        getattr throws AttributeError
      - Any assignment must be not None.


  - Setting a value to None doesn't "unset" a value.  (That's what del is for.)  And you can't
    del a value if required=True, nullable=False, default=None.  That should raise
    OperationNotAllowedError.

  - If a field is not required, del does *not* "unmask" the default value.  Instead, del
    removes the value from the object entirely.  To get back the default value, need to recreate
    the object.  Entity.from_objects(old_object)


  - Disabling in_dump is a "hard" setting, in that with it disabled the field will never get
    dumped.  With it enabled, the field may or may not be dumped depending on its value and other
    settings.

  - Required is a "hard" setting, in that if True, a valid value or default must be provided. None
    is only a valid value or default if nullable is True.

  - In general, nullable means that None is a valid value.
    - getattr returns None instead of raising Attribute error
    - If in_dump, field is given with null value.
    - If default is not None, assigning None clears a previous assignment. Future getattrs return
      the default value.
    - What does nullable mean with default=None and required=True? Does instantiation raise
      an error if assignment not made on init? Can IntField(nullable=True) be init'd?

  - If required=False and nullable=False, field will only be in dump if field!=None.
    Also, getattr raises AttributeError.
  - If required=False and nullable=True, field will be in dump if field==None.

  - What does required and default mean?
  - What does required and default and nullable mean?
  - If in_dump is True, does default value get dumped:
    - if no assignment, default exists
    - if nullable, and assigned None
  - Can assign None?
  - How does optional validation work with nullable and assigning None?
  - When does gettattr throw AttributeError, and when does it return None?





Examples:
    # ## Chapter 1: Entity and Field Basics ##
    >>> class Color(Enum):
    ...     blue = 0
    ...     black = 1
    ...     red = 2
    >>> class Car(Entity):
    ...     weight = NumberField(required=False)
    ...     wheels = IntField(default=4, validation=lambda x: 3 <= x <= 4)
    ...     color = EnumField(Color)

    >>> # create a new car object
    >>> car = Car(color=Color.blue, weight=4242.42)
    >>> car
    Car(weight=4242.42, color=0)

    >>> # it has 4 wheels, all by default
    >>> car.wheels
    4

    >>> # but a car can't have 5 wheels!
    >>> car.wheels = 5
    Traceback (most recent call last):
    ...
    auxlib.exceptions.ValidationError: Invalid value 5 for wheels

    >>> # we can call .dump() on car, and just get back a standard python dict
    >>> #   actually, it's ordereddict to preserve attribute declaration order
    >>> type(car.dump())
    <class 'collections.OrderedDict'>
    >>> car.dump()
    OrderedDict([('weight', 4242.42), ('wheels', 4), ('color', 0)])

    >>> # and json too
    >>> car.json()
    '{"weight": 4242.42, "wheels": 4, "color": 0}'

    >>> # green cars aren't allowed
    >>> car.color = "green"
    Traceback (most recent call last):
    ...
    auxlib.exceptions.ValidationError: 'green' is not a valid Color

    >>> # but black cars are!
    >>> car.color = "black"
    >>> car.color
    <Color.black: 1>

    >>> # car.color really is an enum, promise
    >>> type(car.color)
    <enum 'Color'>

    >>> # let's do a round-trip marshalling of this thing
    >>> same_car = Car.from_json(car.json())  # or equally Car.from_json(json.dumps(car.dump()))
    >>> same_car == car
    True

    >>> # actually, they're two different instances
    >>> same_car is not car
    True

    >>> # this works too
    >>> cloned_car = Car(**car.dump())
    >>> cloned_car == car
    True

    # ## Chapter 2: Entity and Field Composition ##
    >>> # now let's get fancy
    >>> class Fleet(Entity):
    ...     boss_car = ComposableField(Car)
    ...     cars = ListField(Car)

    >>> # here's our fleet of company cars
    >>> company_fleet = Fleet(boss_car=Car(color='red'), cars=[car, same_car, cloned_car])
    >>> company_fleet.pretty_json()  #doctest: +SKIP
    {
      "boss_car": {
        "color": 2,
        "wheels": 4
      },
      "cars": [
        {
          "color": 1,
          "weight": 4242.42,
          "wheels": 4
        },
        {
          "color": 1,
          "weight": 4242.42,
          "wheels": 4
        },
        {
          "color": 1,
          "weight": 4242.42,
          "wheels": 4
        }
      ]
    }

    >>> # the boss' car is red of course (and it's still an Enum)
    >>> company_fleet.boss_car.color.name
    'red'

    >>> # and there are three cars left for the employees
    >>> len(company_fleet.cars)
    3

    >>> # because we can
    >>> sum(c.weight for c in company_fleet.cars)
    12727.26

    # ## Chapter 3: The del and null weeds ##
    >>> old_date = lambda: dateparse('1982-02-17')
    >>> class CarBattery(Entity):
    ...     # NOTE: default value can be a callable!
    ...     first_charge = DateField(required=False)  # default=None, nullable=False
    ...     latest_charge = DateField(default=old_date, nullable=True)  # required=True
    ...     expiration = DateField(default=old_date, required=False, nullable=False)

    # starting point
    >>> battery = CarBattery()
    >>> battery
    CarBattery()
    >>> battery.json()
    '{"latest_charge": "1982-02-17T00:00:00", "expiration": "1982-02-17T00:00:00"}'

    # first_charge is not assigned a default value. Once one is assigned, it can be deleted,
    #   but it can't be made null.
    >>> battery.first_charge = dateparse('2016-03-23')
    >>> battery
    CarBattery(first_charge=datetime.datetime(2016, 3, 23, 0, 0))
    >>> battery.first_charge = None
    Traceback (most recent call last):
    ...
    auxlib.exceptions.ValidationError: Value for first_charge not given or invalid.
    >>> del battery.first_charge
    >>> battery
    CarBattery()

    # latest_charge can be null, but it can't be deleted. The default value is a callable.
    >>> del battery.latest_charge
    Traceback (most recent call last):
    ...
    AttributeError: The latest_charge field is required and cannot be deleted.
    >>> battery.latest_charge = None
    >>> battery.json()
    '{"latest_charge": null, "expiration": "1982-02-17T00:00:00"}'

    # expiration is assigned by default, can't be made null, but can be deleted.
    >>> battery.expiration
    datetime.datetime(1982, 2, 17, 0, 0)
    >>> battery.expiration = None
    Traceback (most recent call last):
    ...
    auxlib.exceptions.ValidationError: Value for expiration not given or invalid.
    >>> del battery.expiration
    >>> battery.json()
    '{"latest_charge": null}'


"""
from __future__ import absolute_import, division, print_function

from collections import OrderedDict as odict
from datetime import datetime
from functools import reduce
from json import loads as json_loads, dumps as json_dumps
from logging import getLogger
import collections

from enum import Enum

from ._vendor.dateutil.parser import parse as dateparse
from ._vendor.five import with_metaclass, items, values
from ._vendor.six import integer_types, string_types
from .collection import AttrDict
from .exceptions import ValidationError, Raise
from .type_coercion import maybecall

log = getLogger(__name__)

KEY_OVERRIDES_MAP = "__key_overrides__"


class Field(object):
    """
    Fields are doing something very similar to boxing and unboxing
    of c#/java primitives.  __set__ should take a "primitve" or "raw" value and create a "boxed"
    or "programatically useable" value of it.  While __get__ should return the boxed value,
    dump in turn should unbox the value into a primitive or raw value.

    Arguments:
        types_ (primitive literal or type or sequence of types):
        default (any, callable, optional):  If default is callable, it's guaranteed to return a
            valid value at the time of Entity creation.
        required (boolean, optional):
        validation (callable, optional):
        dump (boolean, optional):
    """

    # Used to track order of field declarations. Supporting python 2.7, so can't rely
    #   on __prepare__.  Strategy lifted from http://stackoverflow.com/a/4460034/2127762
    _order_helper = 0

    def __init__(self, default=None, required=True, validation=None, in_dump=True, nullable=False):
        self._default = default if callable(default) else self.box(default)
        self._required = required
        self._validation = validation
        self._in_dump = in_dump
        self._nullable = nullable
        if default is not None:
            self.validate(self.box(maybecall(default)))

        self._order_helper = Field._order_helper
        Field._order_helper += 1

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

    def __get__(self, instance, instance_type):
        try:
            if instance is None:  # if calling from the class object
                val = getattr(instance_type, KEY_OVERRIDES_MAP)[self.name]
            else:
                val = instance.__dict__[self.name]
        except AttributeError:
            log.error("The name attribute has not been set for this field.")
            raise AttributeError("The name attribute has not been set for this field.")
        except KeyError:
            if self.default is not None:
                val = maybecall(self.default)  # default *can* be a callable
            elif self._nullable:
                return None
            else:
                raise AttributeError("A value for {0} has not been set".format(self.name))
        if val is None and not self.nullable:
            # means the "tricky edge case" was activted in __delete__
            raise AttributeError("The {0} field has been deleted.".format(self.name))
        return self.unbox(val)

    def __set__(self, instance, val):
        # validate will raise an exception if invalid
        # validate will return False if the value should be removed
        instance.__dict__[self.name] = self.validate(self.box(val))

    def __delete__(self, instance):
        if self.required:
            raise AttributeError("The {0} field is required and cannot be deleted."
                                 .format(self.name))
        elif not self.nullable:
            # tricky edge case
            # given a field Field(default='some value', required=False, nullable=False)
            # works together with Entity.dump() logic for selecting fields to include in dump
            # `if value is not None or field.nullable`
            instance.__dict__[self.name] = None
        else:
            instance.__dict__.pop(self.name, None)

    def box(self, val):
        return val

    def unbox(self, val):
        return val

    def dump(self, val):
        return val

    def validate(self, val):
        """

        Returns:
            True: if val is valid

        Raises:
            ValidationError
        """
        # note here calling, but not assigning; could lead to unexpected behavior
        if isinstance(val, self._type) and (self._validation is None or self._validation(val)):
                return val
        elif val is None and self.nullable:
            return val
        raise ValidationError(getattr(self, 'name', 'undefined name'), val)

    @property
    def required(self):
        return self.is_required

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

    @property
    def nullable(self):
        return self.is_nullable

    @property
    def is_nullable(self):
        return self._nullable


class IntField(Field):
    _type = integer_types


class StringField(Field):
    _type = string_types


class NumberField(Field):
    _type = integer_types + (float, complex)


class BooleanField(Field):
    _type = bool

    def box(self, val):
        return None if val is None else bool(val)


class DateField(Field):
    _type = datetime

    def box(self, val):
        try:
            return dateparse(val) if isinstance(val, string_types) else val
        except ValueError as e:
            raise ValidationError(val, msg=e)

    def dump(self, val):
        return None if val is None else val.isoformat()


class EnumField(Field):

    def __init__(self, enum_class, default=None, required=True, validation=None,
                 in_dump=True, nullable=False):
        if not issubclass(enum_class, Enum):
            raise ValidationError(None, msg="enum_class must be an instance of Enum")
        self._type = enum_class
        super(self.__class__, self).__init__(default, required, validation, in_dump, nullable)

    def box(self, val):
        if val is None:
            # let the required/nullable logic handle validation for this case
            return None
        try:
            # try to box using val as an Enum name
            return val if isinstance(val, self._type) else self._type(val)
        except ValueError as e1:
            try:
                # try to box using val as an Enum value
                return self._type[val]
            except KeyError:
                raise ValidationError(val, msg=e1)

    def dump(self, val):
        return None if val is None else val.value


class ListField(Field):
    _type = tuple

    def __init__(self, element_type, default=None, required=True, validation=None,
                 in_dump=True, nullable=False):
        self._element_type = element_type
        super(self.__class__, self).__init__(default, required, validation, in_dump, nullable)

    def box(self, val):
        if val is None:
            return None
        elif isinstance(val, string_types):
            raise ValidationError("Attempted to assign a string to ListField {0}"
                                  "".format(self.name))
        elif isinstance(val, collections.Iterable):
            et = self._element_type
            if isinstance(et, type) and issubclass(et, Entity):
                return tuple(v if isinstance(v, et) else et(**v) for v in val)
            else:
                return tuple(val)
        else:
            raise ValidationError(val, msg="Cannot assign a non-iterable value to "
                                           "{0}".format(self.name))

    def unbox(self, val):
        return tuple() if val is None and not self.nullable else val

    def dump(self, val):
        if isinstance(self._element_type, type) and issubclass(self._element_type, Entity):
            return tuple(v.dump() for v in val)
        else:
            return val

    def validate(self, val):
        if val is None:
            if not self.nullable:
                raise ValidationError(self.name, val)
            return None
        else:
            val = super(self.__class__, self).validate(val)
            et = self._element_type
            tuple(Raise(ValidationError(self.name, el, et)) for el in val
                  if not isinstance(el, et))
            return val


class MapField(Field):
    _type = dict
    __eq__ = dict.__eq__
    __hash__ = dict.__hash__


class ComposableField(Field):

    def __init__(self, field_class, default=None, required=True, validation=None,
                 in_dump=True, nullable=False):
        self._type = field_class
        super(self.__class__, self).__init__(default, required, validation, in_dump, nullable)

    def box(self, val):
        if val is None:
            return None
        if isinstance(val, self._type):
            return val
        else:
            # assuming val is a dict now
            try:
                # if there is a key named 'self', have to rename it
                val['slf'] = val.pop('self')
            except KeyError:
                pass  # no key of 'self', so no worries
            return val if isinstance(val, self._type) else self._type(**val)

    def dump(self, val):
        return None if val is None else val.dump()


class EntityType(type):

    @staticmethod
    def __get_entity_subclasses(bases):
        try:
            return [base for base in bases if issubclass(base, Entity) and base is not Entity]
        except NameError:
            # NameError: global name 'Entity' is not defined
            return []

    def __new__(mcs, name, bases, dct):
        # if we're about to mask a field that's already been created with something that's
        #  not a field, then assign it to an alternate variable name
        non_field_keys = (key for key, value in items(dct)
                          if not isinstance(value, Field) and not key.startswith('__'))
        entity_subclasses = EntityType.__get_entity_subclasses(bases)
        if entity_subclasses:
            keys_to_override = [key for key in non_field_keys
                                if any(isinstance(base.__dict__.get(key), Field)
                                       for base in entity_subclasses)]
            dct[KEY_OVERRIDES_MAP] = {key: dct.pop(key) for key in keys_to_override}
        else:
            dct[KEY_OVERRIDES_MAP] = dict()

        return super(EntityType, mcs).__new__(mcs, name, bases, dct)

    def __init__(cls, name, bases, attr):
        super(EntityType, cls).__init__(name, bases, attr)
        cls.__fields__ = odict(cls.__fields__) if hasattr(cls, '__fields__') else odict()
        cls.__fields__.update(sorted(((name, field.set_name(name))
                                      for name, field in cls.__dict__.items()
                                      if isinstance(field, Field)),
                                     key=lambda item: item[1]._order_helper))
        if hasattr(cls, '__register__'):
            cls.__register__()

    @property
    def fields(cls):
        return cls.__fields__.keys()


@with_metaclass(EntityType)
class Entity(object):
    __fields__ = odict()

    def __init__(self, **kwargs):
        for key, field in items(self.__fields__):
            try:
                setattr(self, key, kwargs[key])
            except KeyError:
                # handle the case of fields inherited from subclass but overrode on class object
                if key in getattr(self, KEY_OVERRIDES_MAP):
                    setattr(self, key, getattr(self, KEY_OVERRIDES_MAP)[key])
                elif field.required and field.default is None:
                    raise ValidationError(key, msg="{0} requires a {1} field. Instantiated with "
                                                   "{2}".format(self.__class__.__name__,
                                                                key, kwargs))
            except ValidationError:
                if kwargs[key] is not None or field.required:
                    raise
        self.validate()

    @classmethod
    def create_from_objects(cls, *objects, **override_fields):
        init_vars = dict()
        search_maps = (AttrDict(override_fields), ) + objects
        for key, field in items(cls.__fields__):
            value = find_or_none(key, search_maps)
            if value is not None or field.required:
                init_vars[key] = field.type(value) if field.is_enum else value
        return cls(**init_vars)

    @classmethod
    def from_json(cls, json_str):
        return cls(**json_loads(json_str))

    @classmethod
    def load(cls, data_dict):
        return cls(**data_dict)

    def validate(self):
        # TODO: here, validate should only have to determine if the required keys are set
        try:
            reduce(lambda x, y: y, (getattr(self, name)
                                    for name, field in self.__fields__.items()
                                    if field.required))
        except AttributeError as e:
            raise ValidationError(None, msg=e)
        except TypeError as e:
            if "no initial value" in str(e):
                # TypeError: reduce() of empty sequence with no initial value
                pass
            else:
                raise  # pragma: no cover

    def __repr__(self):
        def _exists(key):
            try:
                getattr(self, key)
                return True
            except AttributeError:
                return False

        def _val(key):
            val = getattr(self, key)
            return repr(val.value) if isinstance(val, Enum) else repr(val)

        def _sort_helper(key):
            field = self.__fields__.get(key)
            return field._order_helper if field is not None else -1

        kwarg_str = ", ".join("{0}={1}".format(key, _val(key))
                              for key in sorted(self.__dict__, key=_sort_helper)
                              if _exists(key))
        return "{0}({1})".format(self.__class__.__name__, kwarg_str)

    @classmethod
    def __register__(cls):
        pass

    def json(self, indent=None, separators=None, **kwargs):
        return json_dumps(self.dump(), indent=indent, separators=separators, **kwargs)

    def pretty_json(self, indent=2, separators=(',', ': '), **kwargs):
        return self.json(indent=indent, separators=separators, **kwargs)

    def dump(self):
        return odict((field.name, field.dump(value))
                     for field, value in ((field, getattr(self, field.name, None))
                                          for field in self.__dump_fields())
                     if value is not None or field.nullable)

    @classmethod
    def __dump_fields(cls):
        if '__dump_fields_cache' not in cls.__dict__:
            cls.__dump_fields_cache = tuple(field for field in values(cls.__fields__)
                                            if field.in_dump)
        return cls.__dump_fields_cache

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        rando_default = 19274656290  # need an arbitrary but definite value if field does not exist
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
        >>> print(find_or_none('g', (d1, d2)))
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
