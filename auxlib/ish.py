# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from logging import getLogger
from textwrap import dedent

log = getLogger(__name__)


def dals(string):
    """dedent and left-strip"""
    return dedent(string).lstrip()
