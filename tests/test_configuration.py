import os

from ddt import ddt, unpack, data
from testtools import TestCase, ExpectedException

import auxlib.configuration
from auxlib.configuration import make_env_key, Configuration, reverse_env_key, LocalYamlSource
from auxlib.exceptions import AssignmentError, NotFoundError
from auxlib.type_coercion import typify


APP_NAME = 'test'
PACKAGE = auxlib.configuration.__package__
data_document = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sample_config.yml')


yaml_source = LocalYamlSource(location=data_document,
                         provides=['new_param', 'foo', 'nonetype', 'bool1', 'bool2', 'bool3'])


@ddt
class UtilityTests(TestCase):
    name_tests = [('firstsecond', 'FIRSTSECOND'),
                  ('first_second', 'FIRST_SECOND'),
                  ('first-second', 'FIRST_SECOND'),
                  ('first second', 'FIRST_SECOND'),
                  ('first second-THird_foURTH', 'FIRST_SECOND_THIRD_FOURTH')]

    @unpack
    @data(*name_tests)
    def test_make_env_name(self, badname, fixedname):
        expected_name = APP_NAME.upper() + '_' + fixedname
        self.assertEqual(expected_name, make_env_key(APP_NAME, badname))

    @data('only', 'simple_lowercase', 'will_work_right')
    def test_reverse_env_key(self, key):
        self.assertEqual(key, reverse_env_key(APP_NAME, make_env_key(APP_NAME, key)))

    @unpack
    @data(('true', True), ('Yes', True), ('yes', True), ('ON', True), ('NO', False),
          ('non', 'non'), ('None', None), ('none', None), ('nonea', 'nonea'), (1, 1), ('1', 1),
          ('11.1', 11.1), ('11.1  ', 11.1), ('  44  ', 44), (12.2, 12.2), (None, None))
    def test_typify_without_hint(self, value, result):
        self.assertEqual(result, typify(value))

    @unpack
    @data(('15', True, bool), ('-1', -1.0, float), ('0', False, bool), ('00.000', False, bool),
          ('00.001', True, bool))
    def test_typify_with_hint(self, value, result, hint):
        self.assertEqual(result, typify(value, hint))

    def test_package_name(self):
        assert PACKAGE == 'auxlib'


@ddt
class BasicConfigTests(TestCase):

    def setUp(self):
        super(BasicConfigTests, self).setUp()
        os.environ[make_env_key(APP_NAME, 'foobaz')] = 'no'
        os.environ[make_env_key(APP_NAME, 'zero')] = '0'
        os.environ[make_env_key(APP_NAME, 'an_int')] = '55'
        os.environ[make_env_key(APP_NAME, 'a_float')] = '55.555'
        os.environ[make_env_key(APP_NAME, 'a_none')] = 'none'
        os.environ[make_env_key(APP_NAME, 'just_a_string')] = 'what say you'
        self.config = Configuration(APP_NAME, PACKAGE, yaml_source)

    @unpack
    @data(('new_param', 42), ('foo', 'bar'), ('nonetype', None), ('bool1', True),
          ('bool2', True), ('bool3', True))
    def test_load_config_file(self, config_name, value):
        self.assertEqual(value, self.config[config_name])
        self.assertEqual(type(value), type(self.config[config_name]))

    @unpack
    @data(('foobaz', False), ('zero', 0), ('an_int', 55), ('a_float', 55.555), ('a_none', None),
          ('just_a_string', 'what say you'))
    def test_load_env_vars(self, config_name, value):
        self.assertEqual(value, self.config[config_name])

    def test_get_attr(self):
        self.assertEqual(False, self.config.foobaz)

    def test_get_attr_not_exist(self):
        with ExpectedException(NotFoundError):
            self.config.not_a_key

    def test_get_item_not_exist(self):
        with ExpectedException(NotFoundError):
            self.config['not_a_key']

    def test_get_method(self):
        self.assertEqual(False, self.config.get('foobaz'))
        self.assertEqual(None, self.config.get('not_there'))
        self.assertEqual(22, self.config.get('not_there', 22))

    def test_set_unset_env(self):
        self.assertFalse('new_key' in self.config)
        self.config.set_env('new_key', 12345)
        self.assertTrue('new_key' in self.config)
        self.assertEqual(12345, self.config.new_key)
        self.config.unset_env('new_key')
        self.assertFalse('new_key' in self.config)
        self.config.set_env('new_key', '0')
        self.assertTrue('new_key' in self.config)
        self.assertEqual(False, self.config.new_key)

    def test_unset_env_and_reload(self):
        self.assertTrue('a_float' in self.config)
        self.config.unset_env('a_float')
        self.assertFalse('a_float' in self.config)

    def test_ensure_required_keys(self):
        required_keys = ('bool1', 'nonetype', )
        self.config = Configuration(APP_NAME, PACKAGE, yaml_source, required_keys)
        required_keys += ('doesnt_exist', )
        self.assertRaises(EnvironmentError, Configuration(APP_NAME, PACKAGE,yaml_source, required_keys).verify)
        os.environ[make_env_key(APP_NAME, 'doesnt_exist')] = 'now it does'
        self.config = Configuration(APP_NAME, PACKAGE, yaml_source, required_keys)
        self.assertEqual('now it does', self.config.doesnt_exist)

    def test_items(self):
        self.assertTrue({('a_none', None), ('bool1', True)}.issubset(set(self.config.items())))

    def test_assignment_lock(self):
        with ExpectedException(AssignmentError):
            self.config['bool2'] = 'false'

    def test_config_no_sources(self):
        config = Configuration(APP_NAME, PACKAGE)
        assert config.foobaz is False
        assert config.zero == 0
        assert config.an_int == 55
        assert config.a_float == 55.555
        assert config.a_none is None
        assert config.just_a_string == 'what say you'

        config.unset_env('an_int')
        with ExpectedException(NotFoundError):
            assert config.an_int == 55

        config.set_env('this_key', 'that value')
        config.set_env('that_key', '42.42')

        assert config.this_key == 'that value'
        assert config.that_key == 42.42

    def test_config_no_sources_required_params(self):
        required_parameters = ('beta', 'theta')
        with ExpectedException(EnvironmentError):
            Configuration(APP_NAME, PACKAGE, required_parameters=required_parameters).verify()





