from numbers import Number
from enum import Enum

import types
from testtools import TestCase, ExpectedException
from ddt import ddt, unpack, data

from auxlib.exceptions import ValidationError

from auxlib.entity import Entity, Field


class ChooseOne(Enum):
    A = 'a'
    B = 'b'
    C = 'c'


class Blank(object):
    pass


class SampleEntity(Entity):
    string_field = Field(types.StringTypes)
    integer_field = Field(42)
    default_string_field = Field('default')
    choice = Field(ChooseOne, default='b')


class DerivedSampleEntity(SampleEntity):
    default_string_field = Field(types.StringTypes)
    choice = Field(ChooseOne, required=False)
    new_field = Field(int)

    def __init__(self, new_field, **kwargs):
        self.new_field = new_field
        super(DerivedSampleEntity, self).__init__(**kwargs)


class EntityTests(TestCase):

    def test_sample_entity(self):
        se = SampleEntity(string_field='bazaar', integer_field=28)
        self.assertEqual('bazaar', se.string_field)
        self.assertEqual(28, se.integer_field)
        self.assertEqual('default', se.default_string_field)
        self.assertEqual('b', se.choice)

    def test_derived_sample_entity(self):
        with ExpectedException(ValidationError):
            DerivedSampleEntity(18, default_string_field='taxi')
        dse = DerivedSampleEntity(18, default_string_field='taxi', string_field='boo')
        self.assertEqual(18, dse.new_field)
        self.assertEqual('taxi', dse.default_string_field)
        self.assertEqual('boo', dse.string_field)

    def test_repr(self):
        se = SampleEntity(integer_field=28, string_field='bazaar')
        se2 = eval(repr(se))
        self.assertEqual(repr(se), repr(se2))

    def test_create_from_objects(self):
        se = SampleEntity(string_field='bazaar', integer_field=28)
        blank = Blank()
        blank.integer_field = 14
        se2 = SampleEntity.create_from_objects(blank, se, string_field='baboon')
        self.assertEqual('baboon', se2.string_field)
        self.assertEqual(14, se2.integer_field)


@ddt
class FieldTests(TestCase):

    @unpack
    @data((str, 'abc'), (unicode, u'abc'), (float, 1.234), (int, 42), (types.NoneType, None),
          (types.StringTypes, u'abc'), (types.StringTypes, 'abc'), (Number, 1.234), (Number, 42), )
    def test_positive_validation_with_multiple_types(self, types_, value):
        field = Field(types_)
        field._validate_types(value)

    @unpack
    @data((int, 'abc'), (float, u'abc'), (str, 1.234), (unicode, 42), (str, None),
          (complex, u'abc'), (Number, 'abc'), (types.StringTypes, 1.234), (float, 42), )
    def test_negative_validation_multiple_types(self, types_, value):
        field = Field(types_)
        with ExpectedException(ValidationError):
            field._validate_types(value)

    def test_custom_validation(self):
        field = Field(int, validation=lambda x: x == 2)
        field.validate(2)
        with ExpectedException(ValidationError):
            field.validate('blah')

    def test_required(self):
        field = Field(ChooseOne, required=False)
        field.validate('c')
        field.validate(None)

        field = Field(int, required=False)
        field.validate(42)
        field.validate(None)


class EnumFieldTests(TestCase):

    def test_enum_field_required(self):
        choice1 = Field(ChooseOne, default=ChooseOne.A)
        self.assertEqual(ChooseOne.A, choice1.default)
        self.assertTrue(choice1.is_required)

        choice1.set_name('choice1')
        self.assertEqual('choice1', choice1.name)

        self.assertTrue(choice1.validate('a'))
        self.assertTrue(choice1.validate('b'))
        self.assertTrue(choice1.validate('c'))

        with ExpectedException(ValidationError):
            self.assertTrue(choice1.validate('d'))
        with ExpectedException(ValidationError):
            self.assertTrue(choice1.validate(2))

    def test_enum_field_not_required(self):
        choice2 = Field(ChooseOne, required=False)
        self.assertEqual(None, choice2.default)
        self.assertFalse(choice2.is_required)

        self.assertTrue(choice2.validate('a'))
        self.assertTrue(choice2.validate('b'))
        self.assertTrue(choice2.validate('c'))

        with ExpectedException(ValidationError):
            self.assertTrue(choice2.validate('d'))
        with ExpectedException(ValidationError):
            self.assertTrue(choice2.validate(2))



