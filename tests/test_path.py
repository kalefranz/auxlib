# -*- coding: utf-8 -*-
import logging
from unittest import TestCase

from auxlib import logz
from auxlib.path import PackageFile, find_file_in_site_packages, open_package_file

log = logging.getLogger(__name__)


class PackageFileTests(TestCase):

    @classmethod
    def setUpClass(cls):
        logz.set_root_level(logging.INFO)
        logz.attach_stderr(logging.DEBUG)
        assert not logz.attach_stderr()

    @classmethod
    def tearDownClass(self):
        logz.detach_stderr()
        assert not logz.detach_stderr()

    def test_find_python_file_in_package(self):
        with PackageFile('path.py', 'auxlib') as fh:
            lines = fh.readlines()
            assert any(line.startswith(b'class PackageFile(object):') for line in lines)

    def test_find_python_file_in_package_subdirectory(self):
        with PackageFile('_vendor/five.py', 'auxlib') as fh:
            lines = fh.readlines()
            assert any(line.startswith(b'PY3 = sys.version_info[0] == 3') for line in lines)

    def test_package_resources_paths(self):
        with PackageFile('AES.py', 'Crypto.Cipher') as fh:
            lines = fh.readlines()
            assert any(line.startswith(b'class AESCipher') for line in lines)

    def test_package_resources_paths_subdirectory(self):
        with PackageFile('Cipher/AES.py', 'Crypto') as fh:
            lines = fh.readlines()
            assert any(line.startswith(b'class AESCipher') for line in lines)

    def test_site_packages_paths(self):
        with open(find_file_in_site_packages('AES.py', 'Crypto.Cipher')) as fh:
            lines = fh.readlines()
            assert any(line.startswith('class AESCipher') for line in lines)

    def test_site_packages_paths_subdirectory(self):
        with open(find_file_in_site_packages('Cipher/AES.py', 'Crypto')) as fh:
            lines = fh.readlines()
            assert any(line.startswith('class AESCipher') for line in lines)

    def test_no_file_found(self):
        self.assertRaises(IOError, open_package_file, 'not-a-file.txt', 'auxlib')
