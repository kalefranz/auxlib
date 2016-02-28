# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from abc import ABCMeta, abstractmethod
from logging import getLogger
from textwrap import dedent

from auxlib._vendor.five import with_metaclass

log = getLogger(__name__)


def dals(string):
    """dedent and left-strip"""
    return dedent(string).lstrip()


@with_metaclass(ABCMeta)
class NonStringIterable(object):
    @abstractmethod
    def __iter__(self):
        while False:
            yield None

    @classmethod
    def __subclasshook__(cls, C):
        if cls is NonStringIterable:
            if any("__iter__" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
