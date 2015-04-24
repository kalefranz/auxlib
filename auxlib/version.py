import os
import re
import subprocess


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
        return re.search('^Version:\s+(\S+)', open('../PKG-INFO', 'r').read(), re.MULTILINE).group(1)

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
                    return "0.0.0"
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


    if os.path.exists('../PKG-INFO'):
        return _get_version_from_pkg_info()

    if os.path.exists('.git'):
        return _get_version_from_git_tag()

    raise RuntimeError("Could not get package version (no .git or PKG-INFO)")


if __name__ == "__main__":
    print(get_version())