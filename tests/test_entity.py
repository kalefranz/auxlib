# -*- coding: utf-8 -*-
import datetime
import dateutil.parser
from enum import Enum
import unittest

from testtools import TestCase, ExpectedException

from auxlib.exceptions import ValidationError

from auxlib.entity import Entity, StringField, IntField, EnumField, ListField, DateField


class Color(Enum):
    Red = 'red'
    Green = 'green'
    Blue = 'blue'
    Black = 'black'


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
    enum_field = ChooseOne.A

    def __init__(self, new_field, **kwargs):
        super(DerivedSampleEntity, self).__init__(new_field=new_field, **kwargs)


class EntityTests(unittest.TestCase):

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
                                  integer_field=14)
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

    def test_load_entity_from_dict(self):
        se = SampleEntity(string_field='bazaar', integer_field=28, enum_field=ChooseOne.B)
        d = se.dump()
        assert d.pop('string_field') == 'bazaar'
        assert d.pop('integer_field') == 28
        assert d.pop('enum_field') == 'b'
        assert d.pop('string_field_w_default') == 'default'
        assert d.pop('integer_field_w_default') == 42
        assert d.pop('enum_field_w_default') == 'b'

        assert len(d) == 0

        se2 = SampleEntity.load(se.dump())

        assert se is not se2
        assert se.string_field == se2.string_field
        assert se.string_field_w_default == se2.string_field_w_default
        assert se.integer_field == se2.integer_field
        assert se.integer_field_w_default == se2.integer_field_w_default
        assert se.enum_field == se2.enum_field
        assert se.enum_field_w_default == se2.enum_field_w_default

        se2.integer_field = 4

        assert se.integer_field != se2.integer_field

    def test_entity_eq_and_hash(self):
        se1 = SampleEntity(string_field='s1', integer_field=82, enum_field=ChooseOne.C)
        se2 = SampleEntity(string_field='s1', integer_field=82, enum_field=ChooseOne.C)
        se3 = SampleEntity(string_field='s', integer_field=82, enum_field=ChooseOne.C)

        assert se1 is not se2
        assert se1 == se2
        assert hash(se1) == hash(se2)

        assert se1 != se3
        assert hash(se1) != hash(se3)

    def test_entity_not_eq_and_hash(self):
        se1 = SampleEntity(string_field='s1', integer_field=82, enum_field=ChooseOne.C)
        de1 = DerivedSampleEntity(18, string_field_w_default='taxi', string_field='boo',
                                  integer_field=14)
        assert not se1 == de1
        assert se1 != de1
        assert hash(se1) != hash(de1)

    def test_inherited_field_set_on_class(self):
        dse = DerivedSampleEntity(18, string_field_w_default='taxi', string_field='boo',
                                  integer_field=14)
        assert dse.enum_field == ChooseOne.A.value

        dse.enum_field = ChooseOne.B
        assert dse.enum_field == ChooseOne.B.value

        dse.enum_field = 'c'
        assert dse.enum_field == ChooseOne.C.value

    def test_inherited_field_set_on_instance_object(self):
        dse = DerivedSampleEntity(18, string_field_w_default='taxi', string_field='boo',
                                  integer_field=14)
        assert dse.integer_field == 14

        with ExpectedException(ValidationError):
            dse.integer_field = 14.4

        dse.integer_field += 14
        assert dse.integer_field == 28

        with ExpectedException(ValidationError):
            dse.integer_field = None

    def test_inherited_field_with_default_value(self):
        dse = DerivedSampleEntity(18, string_field_w_default='taxi', string_field='boo',
                                  integer_field=14)
        assert dse.integer_field_w_default == 42

        dse.integer_field_w_default *= 2
        assert dse.integer_field_w_default == 84

        with ExpectedException(ValidationError):
            dse.integer_field_w_default = 14.4

        with ExpectedException(ValidationError):
            dse.integer_field = None


class MiscFieldTests(TestCase):

    def test_unassigned_name_throws_error(self):
        field = IntField()
        with ExpectedException(AttributeError):
            field.name

        class Clazz(object):
            int_field = IntField()
        clazz = Clazz()
        with ExpectedException(AttributeError):
            clazz.int_field

    def test_invalid_default(self):
        with ExpectedException(ValidationError):
            class Clazz(Entity):
                int_field = IntField('18')

    def test_or_none_field_option(self):
        class Clazz(Entity):
            int_field = IntField(required=False, nullable=True)
        clazz = Clazz()
        assert clazz.int_field is None


class EnumEntity(Entity):
    enum_field = EnumField(Color)
    enum_field_w_default = EnumField(Number, Number.Three)
    enum_field_w_default_wo_required = EnumField(Color, Color.Green, False)
    enum_field_w_xtra_validation = EnumField(Number, 2,
                                             validation=lambda v: v in (Number.Two, Number.Three))
    enum_field_wo_dump = EnumField(Color, Color.Black, in_dump=False)


class EnumFieldTests(TestCase):

    def test_optionless_enum(self):
        ee = EnumEntity(enum_field=Color.Red)
        assert ee.enum_field == 'red'

    def test_assignment(self):
        ee = EnumEntity(enum_field=Color.Red)
        assert ee.enum_field == 'red'
        assert ee.enum_field_w_default == 3
        assert ee.enum_field_w_default_wo_required == 'green'
        assert ee.enum_field_w_xtra_validation == 2
        assert ee.enum_field_wo_dump == 'black'

        ee.enum_field = 'blue'
        ee.enum_field_w_default = 2
        ee.enum_field_w_default_wo_required = 'red'
        ee.enum_field_w_xtra_validation = 3
        ee.enum_field_wo_dump = 'red'

        assert ee.enum_field == 'blue'
        assert ee.enum_field_w_default == 2
        assert ee.enum_field_w_default_wo_required == 'red'
        assert ee.enum_field_w_xtra_validation == 3
        assert ee.enum_field_wo_dump == 'red'

        ee.enum_field = Color.Black
        ee.enum_field_w_default = 0
        ee.enum_field_w_default_wo_required = Color.Black
        ee.enum_field_w_xtra_validation = 2
        ee.enum_field_wo_dump = Color.Black

        assert ee.enum_field == 'black'
        assert ee.enum_field_w_default == 0
        assert ee.enum_field_w_default_wo_required == 'black'
        assert ee.enum_field_w_xtra_validation == 2
        assert ee.enum_field_wo_dump == 'black'

        ee.enum_field_w_default_wo_required = None
        assert ee.enum_field_w_default_wo_required == 'green'

    def test_default(self):
        ee = EnumEntity(enum_field=Color.Red)
        assert ee.enum_field_w_default == 3
        assert ee.enum_field_w_default_wo_required == 'green'

        ee2 = EnumEntity(enum_field=Color.Red, enum_field_w_default=2,
                         enum_field_w_default_wo_required=Color.Blue)
        assert ee2.enum_field_w_default == 2
        assert ee2.enum_field_w_default_wo_required == 'blue'

    def test_required_throws_exception(self):
        with ExpectedException(ValidationError):
            EnumEntity()

    def test_wo_required_throws_exception(self):
        with ExpectedException(ValidationError):
            EnumEntity(enum_field=Color.Red, enum_field_w_default_wo_required=2)

        with ExpectedException(ValidationError):
            ee = EnumEntity(enum_field=Color.Red)
            ee.enum_field_w_default_wo_required = Number.Four

    def test_required(self):
        ee = EnumEntity(enum_field=Color.Red, enum_field_w_default_wo_required='red')
        assert ee.enum_field == 'red'
        assert ee.enum_field_w_default_wo_required == 'red'

        ee.enum_field = Color.Black
        ee.enum_field_w_default_wo_required = 'black'
        assert ee.enum_field == 'black'
        assert ee.enum_field_w_default_wo_required == 'black'

        with ExpectedException(ValidationError):
            EnumEntity(enum_field_w_xtra_validation=Number.Four)

    def test_validation(self):
        with ExpectedException(ValidationError):
            EnumEntity(enum_field='purple')

        ee = EnumEntity(enum_field=Color.Red)
        assert ee.enum_field_w_xtra_validation == 2

        ee.enum_field_w_xtra_validation = 3
        assert ee.enum_field_w_xtra_validation == 3

        with ExpectedException(ValidationError):
            ee.enum_field_w_default = 'red'

        with ExpectedException(ValidationError):
            EnumEntity(enum_field=Color.Red, enum_field_w_xtra_validation=Number.Four)

        with ExpectedException(ValidationError):
            ee.enum_field_w_xtra_validation = 1

    def test_in_dump(self):
        ee = EnumEntity(enum_field=Color.Red)

        d = ee.dump()
        assert 'enum_field_wo_dump' not in d
        assert d.pop('enum_field') == 'red'
        assert d.pop('enum_field_w_default') == 3
        assert d.pop('enum_field_w_default_wo_required') == 'green'
        assert d.pop('enum_field_w_xtra_validation') == 2
        assert len(d) == 0


class StringEntity(Entity):
    field = StringField()
    field_w_default = StringField("spruce")
    field_w_default_wo_required = StringField("elm", False)
    field_w_validation = StringField(validation=lambda v: len(v) <= 6)
    field_w_default_w_validation = StringField("redwood", validation=lambda v: len(v) > 6)
    field_wo_dump = StringField("juniper", in_dump=False)
    field_wo_default_wo_required = StringField(required=False)


class StringEntityNullable(Entity):
    field = StringField(nullable=True)
    field_w_default = StringField("spruce", nullable=True)
    field_w_default_wo_required = StringField("elm", False, nullable=True)
    field_w_validation = StringField(validation=lambda v: len(v) <= 6, nullable=True)
    field_w_default_w_validation = StringField("redwood", validation=lambda v: len(v) > 6,
                                               nullable=True)
    field_wo_dump = StringField("juniper", in_dump=False, nullable=True)
    field_wo_default_wo_required = StringField(required=False, nullable=True)


class StringFieldTests(TestCase):

    def test_set_optional_field_to_none(self):
        sf = StringEntity(field="maple", field_w_validation="oak")
        assert sf.field == "maple"
        assert sf.field_w_default_wo_required == "elm"
        with ExpectedException(AttributeError):
            sf.field_wo_default_wo_required

        with ExpectedException(ValidationError):
            sf.field = None
        sf.field_w_default_wo_required = None
        sf.field_wo_default_wo_required = "birch"
        assert sf.field_w_default_wo_required == "elm"
        assert sf.field_wo_default_wo_required == "birch"

        sf.field_wo_default_wo_required = None
        with ExpectedException(AttributeError):
            sf.field_wo_default_wo_required


    def test_assignment(self):
        sf = StringEntity(field="maple", field_w_validation="oak")
        assert sf.field == "maple"
        assert sf.field_w_default == "spruce"
        assert sf.field_w_default_wo_required == "elm"
        assert sf.field_w_validation == "oak"
        assert sf.field_w_default_w_validation == "redwood"
        assert sf.field_wo_dump == "juniper"

        sf.field = "cherry"
        sf.field_w_default = "lemon"
        sf.field_w_default_wo_required = "orange"
        sf.field_w_validation = "plum"
        sf.field_w_default_w_validation = "coconut"
        sf.field_wo_dump = "pineapple"

        assert sf.field == "cherry"
        assert sf.field_w_default == "lemon"
        assert sf.field_w_default_wo_required == "orange"
        assert sf.field_w_validation == "plum"
        assert sf.field_w_default_w_validation == "coconut"
        assert sf.field_wo_dump == "pineapple"

        sf.field_w_default_wo_required = None  # clear the set value and override with default
        assert sf.field_w_default_wo_required == "elm"

        with ExpectedException(ValidationError):
            sf.field_w_validation = "coconut"

        with ExpectedException(ValidationError):
            sf.field_w_default_w_validation = "plum"

        with ExpectedException(ValidationError):
            StringEntity(field=8)

    def test_assignment_unicode(self):
        sf = StringEntity(field=u"màple", field_w_validation=u"öak")
        assert sf.field == u"màple"
        assert sf.field_w_validation == u"öak"

        sf.field = "cherry"
        sf.field_w_validation = "plum"

        assert sf.field == "cherry"
        assert sf.field_w_validation == "plum"

    def test_in_dump(self):
        sf = StringEntity(field="maple", field_w_validation=u"öak")

        d = sf.dump()
        assert 'field_wo_dump' not in d
        assert d.pop('field') == "maple"
        assert d.pop('field_w_default') == "spruce"
        assert d.pop('field_w_default_wo_required') == "elm"
        assert d.pop('field_w_validation') == u"öak"
        assert d.pop('field_w_default_w_validation') == "redwood"
        assert len(d) == 0

    def test_invalidatable(self):
        with ExpectedException(ValidationError):
            class StringEntity2(Entity):
                bad_field_default = StringField("redwood", validation=lambda v: len(v) < 3)
            StringEntity2()

    def test_nullable_wo_default(self):
        # field
        # field_w_validation
        # field_wo_default_wo_required
        sen = StringEntityNullable()
        assert sen.field is None
        assert sen.field_w_validation is None

        d = sen.dump()
        assert d.pop('field') is None
        assert d.pop('field_w_validation') is None

        # now assign values
        sen.field = 'apple'
        sen.field_w_validation = 'pear'

        with ExpectedException(ValidationError):
            sen.field_w_validation = 'pineapple'

        assert sen.field == 'apple'
        assert sen.field_w_validation == 'pear'

        sen.field = None
        sen.field_w_validation = None

        assert sen.field is None
        assert sen.field_w_validation is None

        d = sen.dump()
        assert d.pop('field') is None
        assert d.pop('field_w_validation') is None

        sen = StringEntityNullable(field='grapefruit')
        assert sen.field == 'grapefruit'
        assert sen.field_w_validation is None

        sen.field = None
        assert sen.field is None

    def test_nullable_w_default(self):
        sen = StringEntityNullable(field_w_default=None, field_w_default_wo_required=None)
        assert sen.field_w_default is None
        assert sen.field_w_default_wo_required is None

        sen = StringEntityNullable()
        assert sen.field_w_default == "spruce"
        assert sen.field_w_default_wo_required == "elm"

        sen.field_w_default = None
        sen.field_w_default_wo_required = None
        assert sen.field_w_default is None
        assert sen.field_w_default_wo_required is None

        # Now, to get the default value back, I have to re-assign the default value!
        sen.field_w_default = "spruce"
        sen.field_w_default_wo_required = "elm"
        assert sen.field_w_default == "spruce"
        assert sen.field_w_default_wo_required == "elm"

    def test_rule(self):
        pass
        # field_wo_default_wo_required
        # If required=False and nullable=True, field will be in dump if field==None.



NOW = datetime.datetime.now()
NOW_CALLABLE = datetime.datetime.now

class DateEntity(Entity):
    field = DateField()
    field_w_default = DateField(NOW)
    field_w_default_callable = DateField(NOW_CALLABLE)
    field_w_default_w_validation = DateField(NOW, validation=lambda v: v >= NOW)


class DateFieldTests(TestCase):

    def test_assignment(self):
        df = DateEntity(field=NOW.isoformat())
        assert df.field == NOW.isoformat()
        assert df.field_w_default == NOW.isoformat()
        assert df.field_w_default_w_validation == NOW.isoformat()

        new_now = datetime.datetime.now()
        df.field = new_now
        df.field_w_default = new_now
        df.field_w_default_w_validation = new_now

        assert df.field == new_now.isoformat()
        assert df.field_w_default == new_now.isoformat()
        assert df.field_w_default_w_validation == new_now.isoformat()

        now_now = datetime.datetime.now()
        df.field = now_now
        df.field_w_default = now_now
        df.field_w_default_w_validation = now_now

        assert df.field == now_now.isoformat()
        assert df.field_w_default == now_now.isoformat()
        assert df.field_w_default_w_validation == now_now.isoformat()

    def test_assignment_error(self):
        df = DateEntity(field=NOW.isoformat())
        with ExpectedException(ValidationError):
            df.field_w_default_w_validation = dateutil.parser.parse('2014')

        with ExpectedException(ValidationError):
            DateEntity(field=NOW.isoformat(),
                       field_w_default_w_validation=dateutil.parser.parse('2014').isoformat())

        with ExpectedException(ValidationError):
            DateEntity(field='not parseable as a date')

        with ExpectedException(ValidationError):
            DateEntity(field=15)

    def test_callable_values(self):
        de = DateEntity(field=NOW_CALLABLE)
        assert isinstance(de.field, basestring)


class ListEntity(Entity):
    field = ListField(basestring)
    field_w_default = ListField((int, long), default=[42, 43])
    field_wo_required = ListField(float, required=False)


class ListFieldTests(TestCase):

    def test_assignment(self):
        le = ListEntity(field=['abc', 'def'])
        assert le.field == tuple(['abc', 'def'])
        assert le.field_w_default == tuple([42, 43])

        le.field = ['ghi', u'jkl', 'mno']
        le.field_w_default = [81, 82, 83, 84]

        assert le.field == tuple(['ghi', u'jkl', 'mno'])
        assert le.field_w_default == tuple([81, 82, 83, 84])

        with ExpectedException(ValidationError):
            le.field = ['ghi', 10, 'mno']

        with ExpectedException(ValidationError):
            le.field_w_default = [81, 84.4, 10]

    def test_assignment_wo_required(self):
        le = ListEntity(field=['abc', 'def'])

        assert not hasattr(le, 'field_wo_required')
        with ExpectedException(AttributeError):
            le.field_wo_required

        le.field_wo_required = [33.3, 44.4]
        assert le.field_wo_required == tuple([33.3, 44.4])

        le.field_wo_required = None

        assert not hasattr(le, 'field_wo_required')
        with ExpectedException(AttributeError):
            le.field_wo_required

