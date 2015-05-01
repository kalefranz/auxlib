#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import re
import subprocess

log = logging.getLogger(__name__)


def get_version():
    """Returns a version string for the current package, derived
    either from the SCM (git currently) or from PKG-INFO.

    This function is expected to run in two contexts. In a development
    context, where .git exists, the version is pulled from git tags
    and written into PKG-INFO to create an sdist or bdist.

    In an installation context, the PKG-INFO file written above is the
    source of version string.

    """

    def _get_version_from_pkg_info():
        #pkg_info = pkg_resources.resource_string(auxlib.__name__, 'PKG-INFO')
        pkg_info = open('PKG-INFO', 'r').read()
        return re.search('^Version:\s+(\S+)', pkg_info, re.MULTILINE).group(1)

    def _get_version_from_git_tag():
        """Return a PEP440-compliant version derived from the git status.
        If that fails for any reason, return the first 7 chars of the changeset hash.
        """

        def _is_dirty():
            try:
                subprocess.check_call(['git', 'diff', '--quiet'])
                subprocess.check_call(['git', 'diff', '--cached', '--quiet'])
                return False
            except subprocess.CalledProcessError:
                return True

        def _get_most_recent_tag():
            try:
                return subprocess.check_output(["git", "describe", "--tags"]).strip()
            except subprocess.CalledProcessError as e:
                if e.returncode == 128:
                    return "0.0.0.0"
                else:
                    raise

        def _get_hash():
            return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()[:7]

        tag = _get_most_recent_tag()
        m = re.match("(?P<xyz>\d+\.\d+\.\d+)(?:-(?P<dev>\d+)-(?P<hash>.+))?", tag)

        version = m.group('xyz')
        if m.group('dev') or _is_dirty():
            version += ".dev{dev}+{hash}".format(dev=m.group('dev') or 0,
                                                 hash=m.group('hash') or _get_hash())

        return version

    def is_git_repo(path):
        if path == '/':
            return False
        else:
            return os.path.isdir(os.path.join(path, '.git')) or is_git_repo(os.path.dirname(path))

    if os.path.isfile('PKG-INFO'):
        return _get_version_from_pkg_info()

    here = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))
    if is_git_repo(here):
        return _get_version_from_git_tag()

    raise RuntimeError("Could not get package version (no .git or PKG-INFO)")


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def requirements(*f):
    return [
        r for r in (
            strip_comments(l) for l in open(
                os.path.join(os.getcwd(), 'requirements', *f)).readlines()
        ) if r]

if __name__ == "__main__":
    print(get_version())