# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from logging import getLogger

from requests import Request
from testtools import TestCase

from auxlib.logz import attach_stderr, detach_stderr, initialize_logging, stringify

log = getLogger(__name__)


class TestLoggingSetup(TestCase):

    def test_basic_stderr(self):
        detach_stderr()
        assert attach_stderr()
        assert not attach_stderr()
        assert detach_stderr()
        assert not detach_stderr()
        assert attach_stderr()

    def test_initialize_logging(self):
        attach_stderr()
        initialize_logging()
        log.error("Very important message.")

class TestStringify(TestCase):

    def test_requests_stringify(self):
        url = "http://jenkins.ci/job/awesome_build/buildWithParameters"
        headers = {"Accpet": "application/json",
                   "Content-Type": "application/json"}
        data = {"GIT_BRANCH": "feature/awesome-feature",
                "GIT_HASH": "abbacadaba1234567890"}
        req = Request('POST', url, headers=headers, json=data).prepare()
        strng = stringify(req)
        log.info(strng)

