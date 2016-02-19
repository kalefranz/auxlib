# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys

here = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(here, "auxlib")

# When executing the setup.py, we need to be able to import ourselves, this
# means that we need to add the src/ directory to the sys.path.
sys.path.insert(0, src_dir)

about = {}
with open(os.path.join(src_dir, "__about__.py")) as f:
    exec(f.read(), about)

with open(os.path.join(src_dir, ".version")) as f:
    version = f.read().strip()

requirements = [
    "python-dateutil",
    "PyYAML",
]


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
        sys.exit(errno)


if sys.version_info < (3, 4):
    requirements.append("enum34")

with open(os.path.join(here, "README.rst")) as f:
    long_description = f.read()

setup(
    name=about["__title__"],
    version=version,

    author=about['__author__'],
    author_email=about['__email__'],
    url=about['__homepage__'],
    license=about['__license__'],

    description=about['__summary__'],
    long_description=long_description,

    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,

    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],

    install_requires=requirements,
    tests_require=["tox"],
    extras_require={
       'crypt': ["pycrypto"],
    },
    cmdclass={
        'test': Tox
    },
)
