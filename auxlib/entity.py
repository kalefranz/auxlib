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






Fields are doing something very similar to boxing and unboxing
of java primitives.  __set__ should take a "primitve" or "raw" value and create a "boxed"
or "programatically useable" value of it.  While __get__ should return the boxed value,
dump in turn should unbox the value into a primitive or raw value.

The process of boxing a complex object of nested primitive values:


ComposableField uses another Entity as its type.






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
    <Color.blue: 0>
    >>> sorted(truck.dump().items())
    [('color', 0), ('weight', 44.4)]

"""
import collections
import datetime
import json
import logging

import dateutil.parser
from enum import Enum

from auxlib.exceptions import ValidationError, Raise
from auxlib.collection import AttrDict
from auxlib.type_coercion import maybecall

log = logging.getLogger(__name__)

KEY_OVERRIDES_MAP = "__key_overrides__"


class Field(object):
    """

    Arguments:
        types_ (primitive literal or type or sequence of types):
        default (any, callable, optional):  If default is callable, it's guaranteed to return a
            valid value at the time of Entity creation.
        required (boolean, optional):
        validation (callable, optional):
        dump (boolean, optional):
    """

    def __init__(self, default=None, required=True, validation=None, in_dump=True, nullable=False):
        self._default = default if callable(default) else self.box(default)
        self._required = required
        self._validation = validation
        self._in_dump = in_dump
        self._nullable = nullable
        if default is not None:
            self.validate(self.box(maybecall(default)))

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
            raise
        except KeyError:
            if self.default is not None:
                val = maybecall(self.default)  # default *can* be a callable
            elif self._nullable:
                return None
            else:
                raise AttributeError("A value for {} has not been set".format(self.name))
        return self.unbox(val)

    def __set__(self, instance, val):
        # validate will raise an exception if invalid
        # validate will return False if the value should be removed
        instance.__dict__[self.name] = self.validate(self.box(val))

    def __delete__(self, instance):
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
        if isinstance(val, self._type):
            if self._validation is None or self._validation(val):
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
    _type = (int, long)


class StringField(Field):
    _type = basestring


class NumberField(Field):
    _type = (int, long, float, complex)


class BooleanField(Field):
    _type = bool

    def box(self, val):
        return None if val is None else bool(val)


class DateField(Field):
    _type = datetime.datetime

    def box(self, val):
        try:
            return dateutil.parser.parse(val) if isinstance(val, basestring) else val
        except ValueError as e:
            raise ValidationError(val, msg=e.message)

    def dump(self, val):
        return None if val is None else val.isoformat()


class EnumField(Field):

    def __init__(self, enum_class, default=None, required=True, validation=None,
                 in_dump=True, nullable=False):
        self._type = enum_class
        super(self.__class__, self).__init__(default, required, validation, in_dump, nullable)

    def box(self, val):
        if val is None:
            return None
        try:
            return val if isinstance(val, self._type) else self._type(val)
        except ValueError as e:
            raise ValidationError(val, msg=e.message)

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
        elif isinstance(val, collections.Iterable):
            et = self._element_type
            if isinstance(et, type) and issubclass(et, Entity):
                return tuple(v if isinstance(v, et) else et(**v) for v in val)
            else:
                return tuple(val)
        else:
            raise ValidationError(val, msg="Cannot assign a non-iterable value to "
                                           "{}".format(self.name))

    def unbox(self, val):
        return tuple() if val is None else val

    def dump(self, val):
        if issubclass(self._element_type, Entity):
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
        non_field_keys = (key for key, value in dct.iteritems()
                          if not isinstance(value, Field) and not key.startswith('__'))
        entity_subclasses = EntityType.__get_entity_subclasses(bases)
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

    @property
    def fields(cls):
        return cls.__fields__.keys()


class Entity(object):
    __metaclass__ = EntityType
    __fields__ = dict()
    # TODO: add arg order to fields like in enum34

    def __init__(self, **kwargs):
        for key, field in self.__fields__.iteritems():
            try:
                setattr(self, key, kwargs[key])
            except KeyError as e:
                # handle the case of fields inherited from subclass but overrode on class object
                if key in getattr(self, KEY_OVERRIDES_MAP, []):
                    setattr(self, key, getattr(self, KEY_OVERRIDES_MAP)[key])
                elif not field.required or field.default is not None:
                    pass
                else:
                    raise ValidationError(key, msg="{} requires a {} field. Instantiated with {}"
                                                   "".format(self.__class__.__name__, key, kwargs))
            except ValidationError:
                if kwargs[key] is None and not field.required:
                    pass
                else:
                    raise
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
    def from_json(cls, json_str):
        return cls(**json.loads(json_str))

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
            raise ValidationError(None, msg=e.message)
        except TypeError as e:
            if "no initial value" in e.message:
                # TypeError: reduce() of empty sequence with no initial value
                pass
            else:
                raise  # pragma: no cover

    def __repr__(self):
        _repr = lambda val: repr(val.value) if isinstance(val, Enum) else repr(val)
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join("{}={}".format(key, _repr(value)) for key, value in self.__dict__.items()))

    @classmethod
    def __register__(cls):
        pass

    def dump(self):
        return {field.name: field.dump(value)
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
        rando_default = 19274656290
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
