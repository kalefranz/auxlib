======
auxlib
======


.. image:: https://img.shields.io/pypi/v/auxlib.svg
   :target: https://pypi.python.org/pypi/auxlib

.. image:: https://travis-ci.org/kalefranz/auxlib.svg?branch=develop
   :target: https://travis-ci.org/kalefranz/auxlib

.. image:: https://ci.appveyor.com/api/projects/status/epk1egfkid8wyd6r/branch/develop?svg=true
   :target: https://ci.appveyor.com/project/kalefranz/auxlib

.. image:: https://codecov.io/github/kalefranz/auxlib/coverage.svg?branch=develop
   :target: https://codecov.io/github/kalefranz/auxlib?branch=develop

.. image:: https://scrutinizer-ci.com/g/kalefranz/auxlib/badges/quality-score.png?b=develop
   :target: https://scrutinizer-ci.com/g/kalefranz/auxlib/?branch=develop
   :alt: Scrutinizer Code Quality

.. image:: https://codeclimate.com/github/kalefranz/auxlib/badges/issue_count.svg
   :target: https://codeclimate.com/github/kalefranz/auxlib
   :alt: Issue Count

.. image:: https://www.quantifiedcode.com/api/v1/project/189a0c406b624aaf8c6ac16b80ff92b9/badge.svg
   :target: https://www.quantifiedcode.com/app/project/189a0c406b624aaf8c6ac16b80ff92b9
   :alt: Code issues

.. image:: https://api.codacy.com/project/badge/grade/5195a5ac49fe49c59a4067b420fa76ad
   :target: https://www.codacy.com/app/kalefranz/auxlib

-------------------------------

Auxlib is an auxiliary library to the python standard library.

The aim is to provide core generic features for app development in python. Auxlib fills in some
python stdlib gaps much like `pytoolz <https://github.com/pytoolz/>`_ has for functional
programming, `pyrsistent <https://github.com/tobgu/pyrsistent/>`_ has for data structures, or
`boltons <https://github.com/mahmoud/boltons/>`_ has generally.

Major areas addressed include:
  - `packaging <http://auxlib.readthedocs.org/en/latest/reference/auxlib.packaging.html>`_
       package versioning, with a clean and less invasive alternative to versioneer
  - `entity <http://auxlib.readthedocs.org/en/latest/reference/auxlib.entity.html>`_
       robust base class for type-enforced data models and transfer objects
  - `type_coercion <http://auxlib.readthedocs.org/en/latest/reference/auxlib.type_coercion.html>`_
       intelligent type coercion utilities
  - `configuration <http://auxlib.readthedocs.org/en/latest/reference/auxlib.configuration.html>`_
       a map implementation designed specifically to hold application configuration and
       context information
  - `factory <http://auxlib.readthedocs.org/en/latest/reference/auxlib.factory.html>`_
       factory pattern implementation
  - `path <http://auxlib.readthedocs.org/en/latest/reference/auxlib.path.html>`_
       file path utilities especially helpful when working with various python package formats
  - `logz <http://auxlib.readthedocs.org/en/latest/reference/auxlib.logz.html>`_
       logging initialization routines to simplify python logging setup
  - `crypt <http://auxlib.readthedocs.org/en/latest/reference/auxlib.crypt.html>`_
       simple, but correct, pycrypto wrapper
