# -*- coding: utf-8 -*-
import logging
import os
import pkg_resources
import site
import sys

log = logging.getLogger(__name__)


def site_packages_paths():
    if hasattr(sys, 'real_prefix'):
        # in a virtualenv
        log.debug('searching virtualenv')
        return [p for p in sys.path if p.endswith('site-packages')]
    else:
        # not in a virtualenv
        log.debug('searching outside virtualenv')
        return site.getsitepackages()


class PackageFile(object):

    def __init__(self, file_path, package_name=None):
        self.file_path = file_path
        self.package_name = package_name

    def __enter__(self):
        self.file_handle = open_package_file(self.file_path, self.package_name)
        return self.file_handle

    def __exit__(self, type, value, traceback):
        self.file_handle.close()


def open_package_file(file_path, package_name):
    file_path = expand(file_path)

    # look for file at relative path
    if os.path.exists(file_path):
        log.info("found real file {}".format(file_path))
        return open(file_path)

    # look for file in package resources
    if package_name and pkg_resources.resource_exists(package_name, file_path):
        log.info("found package resource file {} for package {}".format(file_path, package_name))
        return pkg_resources.resource_stream(package_name, file_path)

    # look for file in site-packages
    package_path = package_name.replace('.', '/')
    for site_packages_path in site_packages_paths():
        test_path = os.path.join(site_packages_path, package_path, file_path)
        if os.path.exists(test_path):
            log.info("found site-package file {} for package {}".format(file_path, package_name))
            return open(test_path)

    msg = "file for module [{}] cannot be found at path {}".format(package_name, file_path)
    log.error(msg)
    raise IOError(msg)


def expand(path):
    return os.path.normpath(os.path.expanduser(os.path.expandvars(path)))
