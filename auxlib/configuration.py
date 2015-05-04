#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A specialized map implementation to manage configuration and context information.

Features:
  * Uses YAML configuration files
  * Use environment variables to override config file
  * Can pass a list of required parameters at initialization
  * Works with encrypted files
  * Accepts multiple config files
  * Can query information from consul

"""
import logging
import sys

import os
import pkg_resources
import site
import yaml

from auxlib.decorators import memoize, memoizemethod
from auxlib.exceptions import AssignmentError
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


def get_site_packages_paths():
    if hasattr(sys,'real_prefix'):
        # in a virtualenv
        return [p for p in sys.path if p.endswith('site-packages')]
    else:
        # not in a virtualenv
        return site.getsitepackages()


def find_config_file(config_file, package_name):
    config_file = os.path.normpath(os.path.expandvars(os.path.expanduser(config_file)))

    if os.path.exists(config_file):
        return open(config_file)

    if pkg_resources.resource_exists(package_name, config_file):
        return pkg_resources.resource_stream(package_name, config_file)

    package_path = package_name.replace('.', '/')
    for site_packages_path in get_site_packages_paths():
        test_path = os.path.join(site_packages_path, package_path, config_file)
        if os.path.exists(test_path):
            return open(test_path)

    log.error("config file for module [{}] cannot be found at path [{}]"
              "".format(package_name, config_file))
    raise IOError("config file for module [{}] cannot be found at path [{}]"
                  "".format(package_name, config_file))


class Configuration(object):
    """A specialized map implementation to manage configuration and context information. Values
    can be accessed (read, not assigned) as either a dict lookup (e.g. `config[key]`)are as an
    attribute (e.g. `config.key`).

    This class makes the foundational assumption of a yaml configuration file, a values in yaml
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

        >>> context = Configuration('foo')
        >>> context.bar, type(context.bar)
        (22, <type 'int'>)
        >>> context['baz'], type(context['baz'])
        (True, <type 'bool'>)
        >>> context.bang, type(context.bang)
        ('monkey', <type 'str'>)

        >>> context = Configuration('foo', required_parameters=('bar', 'boink'))
        Traceback (most recent call last):
        ...
        EnvironmentError: Required key(s) not found in environment
          or configuration file [None].
          Missing Keys: ['boink']

    """

    def __init__(self, app_name, config_file=None, required_parameters=None, package_name=__package__):
        self._config_map = dict()
        self._registered_env_keys = set()

        self.app_name = app_name
        self._required_keys = set(required_parameters if required_parameters is not None else [])

        self.__config_file = config_file
        self.__package_name = package_name
        self.package_name = package_name

        # now lock instance object to not allow further assignment
        self.__setattr__ = self.__lock_assignment

        self.reload()

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

    def reload(self):
        """Reloads the configuration from the file and environment variables. Useful if using
        `os.environ` instead of this class' `set_env` method, or if the underlying configuration
        file is changed externally.
        """
        self.__load_config_file()
        self.__load_environment_keys()
        self.__ensure_required_keys()

    @memoizemethod  # memoized for performance; always use self.set_env() instead of os.setenv()
    def __getitem__(self, key):
        # This method is complicated by the fact that `None` is a valid python-yaml type.
        key_in_file = key in self._config_map
        from_file = self._config_map.get(key, None)

        from_env = os.getenv(make_env_key(self.app_name, key), None)
        if from_env is not None:
            # give type hint from type in config file if possible
            return typify(from_env, type(from_file) if key_in_file else None)
        elif key_in_file:
            return from_file
        else:
            raise KeyError("Key [{}] not found in configuration.".format(key))

    def __getattr__(self, key):
        return self[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        raise AssignmentError()

    def __lock_assignment(self, key, value):
        raise AssignmentError()

    def __iter__(self):
        for key in self._registered_env_keys | set(self._config_map.keys()):
            yield key

    def items(self):
        for key in self:
            yield key, self[key]

    # def _attach_config_file(self, config_file):
    #     if config_file is not None:
    #         try:
    #             self.__config_file_type = config_type = ('absolute_path'
    #                                                      if config_file.startswith('/')
    #                                                      else 'pkg_resource')
    #             self.__config_file = os.path.expandvars(os.path.expanduser(config_file))
    #             if config_type == 'absolute_path':
    #                 if not os.path.exists(self.__config_file):
    #                     raise IOError()
    #             if config_type == 'pkg_resource':
    #                 if not pkg_resources.resource_exists('ttam.transcomm', self.__config_file):
    #                     raise IOError()
    #         except IOError:
    #             log.error("config file type [{}] cannot be found at path [{}]"
    #                       "".format(self.__config_file_type, self.__config_file))
    #             raise IOError("config file type [{}] cannot be found at path [{}]"
    #                           "".format(self.__config_file_type, self.__config_file))
    #         except AttributeError:
    #             raise IOError("config_file not found or must be a file path <type 'str'>.\n"
    #                           "   Found {} instead.".format(config_file))

    def __load_config_file(self):
        if self.__config_file is None:
            return
        self._config_map = dict()
        file_handle = find_config_file(self.__config_file, self.__package_name)
        self._config_map.update(yaml.load(file_handle))
        self._clear_memoization()
        file_handle.close()

        # if self.__config_file_type == 'pkg_resource':
        #     conf_file = pkg_resources.resource_stream('ttam.transcomm', self.__config_file)
        #     self._config_map.update(yaml.load(conf_file))
        #     self._clear_memoization()
        #     conf_file.close()
        # else:
        #     with open(self.__config_file, 'r') as conf_file:
        #         self._config_map.update(yaml.load(conf_file))
        #         self._clear_memoization()

    def __load_environment_keys(self):
        self._registered_env_keys = set()
        app_prefix = self.app_name.upper() + '_'
        for env_key in os.environ:
            if env_key.startswith(app_prefix):
                self._registered_env_keys.add(reverse_env_key(self.app_name, env_key))
        self._clear_memoization()

    def __ensure_required_keys(self):
        available_keys = self._registered_env_keys | set(self._config_map.keys())
        missing_keys = self._required_keys - available_keys
        if missing_keys:
            raise EnvironmentError("Required key(s) not found in environment\n"
                                   "  or configuration file [{0}].\n"
                                   "  Missing Keys: {1}".format(self.__config_file,
                                                                list(missing_keys)))

    def _clear_memoization(self):
        self.__dict__.pop('_memoized_results', None)


A = Configuration('app')