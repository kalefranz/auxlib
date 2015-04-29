from enum import Enum

from testtools import TestCase, ExpectedException
from ddt import ddt, unpack, data

from auxlib.exceptions import ValidationError

from auxlib.entity import Entity, StringField, IntField, EnumField


class Color(Enum):
    red = 'red'
    green = 'green'
    blue = 'blue'
    black = 'black'


class Number(Enum):
    Zero, One, Two, Three, Four = range(5)


class ChooseOne(Enum):
    A = 'a'
    B = 'b'
    C = 'c'


class Blank(object):
    pass


class SampleEntity(Entity):
    string_field = StringField()
    string_field_w_default = StringField('default')
    integer_field = IntField()
    integer_field_w_default = IntField(42)
    enum_field = EnumField(ChooseOne)
    enum_field_w_default = EnumField(ChooseOne, ChooseOne.B)


class DerivedSampleEntity(SampleEntity):
    string_field_w_default = StringField('new_default')
    choice = EnumField(ChooseOne, required=False)
    new_field = IntField()

    def __init__(self, new_field, **kwargs):
        super(DerivedSampleEntity, self).__init__(new_field=new_field, **kwargs)


class EntityTests(TestCase):

    def test_sample_entity(self):
        se = SampleEntity(string_field='bazaar', integer_field=28, enum_field=ChooseOne.B)
        self.assertEqual('bazaar', se.string_field)
        self.assertEqual(28, se.integer_field)
        self.assertEqual('default', se.string_field_w_default)
        self.assertEqual('b', se.enum_field)

    def test_derived_sample_entity(self):
        with ExpectedException(ValidationError):
            DerivedSampleEntity(18, string_field_w_default='taxi')
        dse = DerivedSampleEntity(18, string_field_w_default='taxi', string_field='boo',
                                  integer_field=14, enum_field=ChooseOne.C)
        self.assertEqual(18, dse.new_field)
        self.assertEqual('taxi', dse.string_field_w_default)
        self.assertEqual('boo', dse.string_field)

    def test_repr(self):
        se = SampleEntity(integer_field=28, string_field='bazaar', enum_field=ChooseOne.C)
        se2 = eval(repr(se))
        self.assertEqual(repr(se), repr(se2))

    def test_create_from_objects(self):
        se = SampleEntity(string_field='bazaar', integer_field=28, enum_field=ChooseOne.A)
        blank = Blank()
        blank.integer_field = 14
        se2 = SampleEntity.create_from_objects(blank, se, string_field='baboon')
        self.assertEqual('baboon', se2.string_field)
        self.assertEqual(14, se2.integer_field)


# @ddt
# class FieldTests(TestCase):
#
#     @unpack
#     @data((str, 'abc'), (unicode, u'abc'), (float, 1.234), (int, 42), (types.NoneType, None),
#           (types.StringTypes, u'abc'), (types.StringTypes, 'abc'), (Number, 1.234), (Number, 42), )
#     def test_positive_validation_with_multiple_types(self, types_, value):
#         field = Field(types_)
#         field._validate_types(value)
#
#     @unpack
#     @data((int, 'abc'), (float, u'abc'), (str, 1.234), (unicode, 42), (str, None),
#           (complex, u'abc'), (Number, 'abc'), (types.StringTypes, 1.234), (float, 42), )
#     def test_negative_validation_multiple_types(self, types_, value):
#         field = Field(types_)
#         with ExpectedException(ValidationError):
#             field._validate_types(value)
#
#     def test_custom_validation(self):
#         field = Field(int, validation=lambda x: x == 2)
#         field.validate(2)
#         with ExpectedException(ValidationError):
#             field.validate('blah')
#
#     def test_required(self):
#         field = EnumField(ChooseOne, required=False)
#         field = ChooseOne.c
#         field.validate('c')
#         field.validate(None)
#
#         field = IntField(required=False)
#         field.validate(42)
#         field.validate(None)


# class EnumFieldTests(TestCase):
#
#     def test_enum_field_required(self):
#         choice1 = EnumField(ChooseOne, default=ChooseOne.A)
#         self.assertEqual(ChooseOne.A, choice1.default)
#         self.assertTrue(choice1.is_required)
#
#         choice1.set_name('choice1')
#         self.assertEqual('choice1', choice1.name)
#
#         self.assertTrue(choice1.validate(ChooseOne('a')))
#         self.assertTrue(choice1.validate(ChooseOne('b')))
#         self.assertTrue(choice1.validate(ChooseOne('c')))
#
#         with ExpectedException(ValidationError):
#             self.assertTrue(choice1.validate(ChooseOne('d')))
#         with ExpectedException(ValidationError):
#             self.assertTrue(choice1.validate(ChooseOne(2)))
#
#     def test_enum_field_not_required(self):
#         choice2 = EnumField(ChooseOne, required=False)
#         self.assertEqual(None, choice2.default)
#         self.assertFalse(choice2.is_required)
#
#         self.assertTrue(choice2.validate(ChooseOne('a')))
#         self.assertTrue(choice2.validate(ChooseOne('b')))
#         self.assertTrue(choice2.validate(ChooseOne('c')))
#
#         with ExpectedException(ValidationError):
#             self.assertTrue(choice2.validate(ChooseOne('d')))
#         with ExpectedException(ValidationError):
#             self.assertTrue(choice2.validate(ChooseOne(2)))



