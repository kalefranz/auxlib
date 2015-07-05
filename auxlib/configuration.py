# -*- coding: utf-8 -*-
"""A specialized map implementation to manage configuration and context information.

Features:
  * Uses YAML configuration files
  * Use environment variables to override configs
  * Can pass a list of required parameters at initialization
  * Works with encrypted files
  * Accepts multiple config files
  * Can query information from consul
  * Does type coercion on strings
  *

"""
import logging
import os

from auxlib.collection import listify
from auxlib.decorators import memoize, memoizemethod
from auxlib.exceptions import AssignmentError, NotFoundError
from auxlib.path import PackageFile
from auxlib.type_coercion import typify


log = logging.getLogger(__name__)


@memoize
def make_env_key(app_name, key):
    """Creates an environment key-equivalent for the given key"""
    key = key.replace('-', '_').replace(' ', '_')
    return "_".join((x.upper() for x in (app_name, key)))


@memoize
def reverse_env_key(app_name, key):
    app = app_name.upper() + '_'
    assert key.startswith(app), "{} is not a(n) {} environment key".format(key, app)
    return key[len(app):].lower()


class Configuration(object):
    """A map implementation to manage configuration and context information. Values
    can be accessed (read, not assigned) as either a dict lookup (e.g. `config[key]`) or as an
    attribute (e.g. `config.key`).

    This class makes the foundational assumption of a yaml configuration file, as values in yaml
    are typed.

    This class allows overriding configuration keys with environment variables. Given an app name
    `foo` and a config parameter `bar: 15`, setting a `FOO_BAR` environment variable to `22` will
    override the value of `bar`. The type of `22` remains `int` because the underlying value of
    `15` is used to infer the type of the `FOO_BAR` environment variable. When an underlying
    parameter does not exist in a config file, the type is intelligently guessed.

    Args:
        app_name (str)
        config_sources (str or list, optional)
        required_parameters (iter, optional)

    Raises:
        InitializationError: on instantiation, when `required_parameters` are not found
        warns: on instantiation, when a given `config_file` cannot be read
        NotFoundError: when requesting a key that does not exist

    Examples:
        >>> for (key, value) in [('FOO_BAR', 22), ('FOO_BAZ', 'yes'), ('FOO_BANG', 'monkey')]:
        ...     os.environ[key] = str(value)

        >>> context = Configuration('foo', __package__)
        >>> context.bar, type(context.bar)
        (22, <type 'int'>)
        >>> context['baz'], type(context['baz'])
        (True, <type 'bool'>)
        >>> context.bang, type(context.bang)
        ('monkey', <type 'str'>)

        >>> context = Configuration('foo', __package__, required_parameters=('bar', 'boink')).verify()
        Traceback (most recent call last):
        ...
        EnvironmentError: Required key(s) not found in environment
          or configuration sources.
          Missing Keys: ['boink']

    """

    def __init__(self, app_name, package, config_sources=None, required_parameters=None):
        self.app_name = app_name
        self.package = package
        self.__initial_load = True

        self.__sources = list()
        self._config_map = dict()
        self._registered_env_keys = set()
        self._required_keys = set(listify(required_parameters))

        self.append_sources(config_sources, force_reload=True)
        self.__load_environment_keys()

    def append_sources(self, config_sources, parent_source=None, force_reload=False):
        for source in listify(config_sources):
            source.parent_config = self
            self.__load_source(source, force_reload)
            source.parent_source = parent_source
            self.__sources.append(source)

    def verify(self):
        self.__ensure_required_keys()
        return self

    def set_env(self, key, value):
        """Sets environment variables by prepending the app_name to `key`. Also registers the
        environment variable with the instance object preventing an otherwise-required call to
        `reload()`.
        """
        os.environ[make_env_key(self.app_name, key)] = str(value)  # must coerce to string
        self._registered_env_keys.add(key)
        self._clear_memoization()

    def unset_env(self, key):
        """Removes an environment variable using the prepended app_name convention with `key`."""
        os.environ.pop(make_env_key(self.app_name, key), None)
        self._registered_env_keys.discard(key)
        self._clear_memoization()

    def _reload(self, force=False):
        """Reloads the configuration from the file and environment variables. Useful if using
        `os.environ` instead of this class' `set_env` method, or if the underlying configuration
        file is changed externally.
        """
        self._config_map = dict()
        self._registered_env_keys = set()
        self.__reload_sources(force)
        self.__load_environment_keys()
        self.__ensure_required_keys()
        self._clear_memoization()

    @memoizemethod  # memoized for performance; always use self.set_env() instead of os.setenv()
    def __getitem__(self, key):
        if key in self._registered_env_keys:
            from_env = os.getenv(make_env_key(self.app_name, key))
            from_sources = self._config_map.get(key, None)
            return typify(from_env, type(from_sources) if from_sources is not None else None)
        else:
            try:
                return self._config_map[key]
            except KeyError as e:
                raise NotFoundError(e.message)

    def __getattr__(self, key):
        return self[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        raise AssignmentError()

    def __iter__(self):
        for key in self._registered_env_keys | set(self._config_map.keys()):
            yield key

    def items(self):
        for key in self:
            yield key, self[key]

    def __load_source(self, source, force_reload=False):
        if force_reload and source.parent_source:
            return

        items = source.dump(force_reload)
        if source.provides and not set(source.provides).issubset(items):
            raise

        additional_requirements = items.pop('additional_requirements', None)
        if isinstance(additional_requirements, basestring):
            additional_requirements = additional_requirements.split(',')
        self._required_keys |= set(listify(additional_requirements))

        additional_sources = items.pop('additional_sources', None)

        self._config_map.update(items)

        if additional_sources:
            for class_name, kwargs in additional_sources.items():
                additional_source = getattr(globals(), class_name)(**kwargs)
                self.append_sources(additional_source, source)

    def __load_environment_keys(self):
        app_prefix = self.app_name.upper() + '_'
        for env_key in os.environ:
            if env_key.startswith(app_prefix):
                self._registered_env_keys.add(reverse_env_key(self.app_name, env_key))
                # We don't actually add values to _config_map here. Rather, they're pulled
                # directly from os.environ at __getitem__ time. This allows for type casting
                # environment variables if possible.

    def __ensure_required_keys(self):
        available_keys = self._registered_env_keys | set(self._config_map.keys())
        missing_keys = self._required_keys - available_keys
        if missing_keys:
            raise EnvironmentError("Required key(s) not found in environment\n"
                                   "  or configuration sources.\n"
                                   "  Missing Keys: {}".format(list(missing_keys)))

    def _clear_memoization(self):
        self.__dict__.pop('_memoized_results', None)


class Source(object):
    _items = None
    _provides = None
    _parent_source = None

    @property
    def provides(self):
        return self._provides

    @property
    def items(self):
        return self.dump()

    def load(self):
        """Must return a key, value dict"""
        raise NotImplementedError()  # pragma: no cover

    def dump(self, force_reload=False):
        if self._items is None or force_reload:
            self._items = self.load()
        return self._items

    @property
    def parent_config(self):
        return self._parent_config

    @parent_config.setter
    def parent_config(self, parent_config):
        self._parent_config = parent_config

    @property
    def parent_source(self):
        return self._parent_source

    @parent_source.setter
    def parent_source(self, parent_source):
        self._parent_source = parent_source


class YamlSource(Source):

    def __init__(self, location, package_name=None, provides=None):
        self._location = location
        self._package_name = package_name
        self._provides = provides if provides else None

    def load(self):
        with PackageFile(self._location, self._package_name
                                         or self.parent_config.package) as fh:
            import yaml
            contents = yaml.load(fh)
            if self.provides is None:
                return contents
            else:
                return {key: contents[key] for key in self.provides}


class EnvironmentSource(Source):

    def __init__(self, provides):
        self._provides = provides

    def load(self):
        return {key: os.environ[key] for key in self.provides}
