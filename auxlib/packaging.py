# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from logging import getLogger
from os.path import basename, dirname, join, isdir
from pkg_resources import resource_string
from re import match
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist
from setuptools.command.test import test as TestCommand
from subprocess import CalledProcessError, check_call, check_output
from sys import exit

from .path import absdirname

log = getLogger(__name__)


def _get_version_from_pkg_info(package_name):
    return resource_string(package_name, '.version')


def _get_version_from_git_tag():
    """Return a PEP440-compliant version derived from the git status.
    If that fails for any reason, return the first 7 chars of the changeset hash.
    """

    def _is_dirty():
        try:
            check_call(['git', 'diff', '--quiet'])
            check_call(['git', 'diff', '--cached', '--quiet'])
            return False
        except CalledProcessError:
            return True

    def _get_most_recent_tag():
        try:
            return check_output(["git", "describe", "--tags"]).strip()
        except CalledProcessError as e:
            if e.returncode == 128:
                return "0.0.0.0"
            else:
                raise

    def _get_hash():
        try:
            return check_output(["git", "rev-parse", "HEAD"]).strip()[:7]
        except CalledProcessError:
            return

    tag = _get_most_recent_tag()
    m = match("(?P<xyz>\d+\.\d+\.\d+)(?:-(?P<dev>\d+)-(?P<hash>.+))?", tag)

    version = m.group('xyz')
    if m.group('dev') or _is_dirty():
        version += ".dev{dev}+{hash}".format(dev=m.group('dev') or 0,
                                             hash=m.group('hash') or _get_hash())
    return version


def is_git_repo(path, package):
    if path == '/' or basename(path) == package:
        return False
    else:
        return isdir(join(path, '.git')) or is_git_repo(dirname(path), package)


def get_version(file, package):
    """Returns a version string for the current package, derived
    either from the SCM (git currently) or from PKG-INFO.

    This function is expected to run in two contexts. In a development
    context, where .git/ exists, the version is pulled from git tags
    and written into PKG-INFO to create an sdist or bdist.

    In an installation context, the PKG-INFO file written above is the
    source of version string.

    """
    here = absdirname(file)
    if is_git_repo(here, package):
        return _get_version_from_git_tag()

    # fall back to .version file
    version_from_pkg = _get_version_from_pkg_info(package)
    if version_from_pkg:
        return version_from_pkg

    raise RuntimeError("Could not get package version (no .git or .version file)")


class BuildPyCommand(build_py):
    def run(self):
        # root = get_root()
        # cfg = get_config_from_root(root)
        # versions = get_versions()
        build_py.run(self)
        # locate .version in the new build/ directory and replace it with an updated value
        target_version_file = join(self.build_lib, self.distribution.metadata.name, ".version")
        print("UPDATING %s" % target_version_file)
        with open(target_version_file, 'w') as f:
            f.write(self.distribution.metadata.version)


class SdistCommand(sdist):
    def run(self):
        return sdist.run(self)

    def make_release_tree(self, base_dir, files):
        sdist.make_release_tree(self, base_dir, files)
        target_version_file = join(base_dir, self.distribution.metadata.name, ".version")
        print("UPDATING %s" % target_version_file)
        with open(target_version_file, 'w') as f:
            f.write(self.distribution.metadata.version)


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        else:
            args = ''
        errno = tox.cmdline(args=args)
        exit(errno)


if __name__ == "__main__":
    print(get_version(__file__, __package__))
