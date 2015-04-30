from enum import Enum

from testtools import TestCase, ExpectedException

from auxlib.exceptions import ValidationError

from auxlib.entity import Entity, StringField, IntField, EnumField, Field


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


# class FieldTests(TestCase):
#
#     def test_cant_instantiate_field(self):
#         f = Field()

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

        with ExpectedException(ValidationError):
            ee.enum_field_w_default_wo_required = None

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
        assert 'enum_field_w_default_wo_required' not in d
        assert 'enum_field_wo_dump' not in d
        assert d.pop('enum_field') == 'red'
        assert d.pop('enum_field_w_default') == 3
        assert d.pop('enum_field_w_xtra_validation') == 2
        assert len(d) == 0




class StringEntity(Entity):
    field = StringField()
    field_w_default = StringField("spruce")
    field_w_default_wo_required = StringField("elm", False)
    field_w_validation = StringField(validation=lambda v: len(v) <= 6)
    field_w_default_w_validation = StringField("redwood", validation=lambda v: len(v) > 6)
    field_wo_dump = StringField("juniper", in_dump=False)


class StringFieldTests(TestCase):

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

        with ExpectedException(ValidationError):
            sf.field_w_default_wo_required = None

        with ExpectedException(ValidationError):
            sf.field_w_validation = "coconut"

        with ExpectedException(ValidationError):
            sf.field_w_default_w_validation = "plum"

        with ExpectedException(ValidationError):
            StringEntity(field=8)

    def test_in_dump(self):
        sf = StringEntity(field="maple", field_w_validation="oak")

        d = sf.dump()
        assert 'field_w_default_wo_required' not in d
        assert 'field_wo_dump' not in d
        assert d.pop('field') == "maple"
        assert d.pop('field_w_default') == "spruce"
        assert d.pop('field_w_validation') == "oak"
        assert d.pop('field_w_default_w_validation') == "redwood"
        assert len(d) == 0