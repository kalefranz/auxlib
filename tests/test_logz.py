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

# class TestStringify(TestCase):
#
#     def basic_test(self):
#         jenkins_url = "http://jenkins-{}.23andme.io".format(repo.replace('23andme/', '', 1))
#         job_name = branch.replace('origin/', '', 1).split('/')[0]
#         url = ("{}/job/{}_build/buildWithParameters".format(jenkins_url, job_name))
#
#         data = {"GIT_BRANCH": branch if branch.startswith('origin/') else "origin/{}".format(branch),
#                 "GIT_HASH": commit_hash}
#         req = Request('POST', url, data=data).prepare()
#
#         stringify(req)
