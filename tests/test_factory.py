from testtools import TestCase, ExpectedException

from auxlib.configuration import Configuration
from auxlib.exceptions import InitializationError
from auxlib.factory import Factory


class AppContext(Configuration):
    pass

appcontext = AppContext('foo')

class SomeFactory(Factory):

    def do_something(self):
        raise NotImplementedError()


class ThisImplementation(SomeFactory):

    def __init__(self, context):
        self._value = context.test_value

    def do_something(self):
        return self._value


class ThatImplementation(SomeFactory):
    do_cache = True

    def __init__(self, context):
        self._value = context.test_value

    def do_something(self):
        return self._value


class AnotherFactory(Factory):

    def do_something(self):
        raise NotImplementedError()


class AnotherImplementation(AnotherFactory):

    def __init__(self, context):
        self._value = context.test_value


class GatewayBaseTests(TestCase):

    def test_get_instance_before_initialization(self):
        with ExpectedException(InitializationError):
            AnotherFactory.factory.get_instance()
        with ExpectedException(InitializationError):
            AnotherFactory.factory.get_instance()
        with ExpectedException(RuntimeError):
            AnotherFactory.factory.initialize(appcontext, ThisImplementation)
        AnotherFactory.factory.initialize(appcontext, AnotherImplementation)
        self.assertTrue(AnotherFactory.factory.get_instance())

    def test_initialize_unregistered_class(self):
        with ExpectedException(RuntimeError):
            SomeFactory.factory.initialize(appcontext, 'NotARegisteredClass')

    def test_cached_instances(self):
        SomeFactory.factory.initialize(appcontext, 'ThatImplementation')
        appcontext.set_env('test_value', 44)
        self.assertEqual(44, SomeFactory().do_something())
        self.assertEqual(44, SomeFactory(ThisImplementation).do_something())
        self.assertEqual(44, SomeFactory('ThatImplementation').do_something())
        self.assertEqual(44, SomeFactory.factory.get_instance().do_something())
        self.assertEqual(44, SomeFactory.factory.get_instance(ThatImplementation).do_something())
        self.assertEqual(44, SomeFactory.factory.get_instance('ThisImplementation').do_something())

        appcontext.set_env('test_value', 88)
        self.assertEqual(44, SomeFactory().do_something())
        self.assertEqual(88, SomeFactory(ThisImplementation).do_something())
        self.assertEqual(44, SomeFactory('ThatImplementation').do_something())
        self.assertEqual(44, SomeFactory.factory.get_instance().do_something())
        self.assertEqual(44, SomeFactory.factory.get_instance(ThatImplementation).do_something())
        self.assertEqual(88, SomeFactory.factory.get_instance('ThisImplementation').do_something())
