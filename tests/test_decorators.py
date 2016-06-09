# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from logging import getLogger
from unittest import TestCase

from auxlib.decorators import classproperty

log = getLogger(__name__)


class AllTheAnswers(object):
    _x = 42
    _y = 43

    def __init__(self, x, y):
        self._x = x
        self._y = y

    @classproperty
    def x(cls):
        return cls._x

    @x.setter
    def x(cls, val):
        cls._x = val

    @classproperty
    def y(cls):
        return cls._y

    @property
    def z(self):
        return 10

class TestClassProperty(TestCase):

    # def test_basic_class_property(self):
    #     assert AllTheAnswers.x == 42
    #
    #     AllTheAnswers.x = 15
    #     assert AllTheAnswers.x == 15
    #     assert AllTheAnswers._x == 42  # the x.setter masks 42
    #
    #     # with ExpectedException(AttributeError):
    #     # AllTheAnswers.y = 16
    #     # assert AllTheAnswers.y == 43
    #
    #     AllTheAnswers._y = 15
    #     assert AllTheAnswers.y == 15  # no y.setter so _y is changed

    def test_instantiated_class_property(self):
        AllTheAnswers.x = 42
        AllTheAnswers._x = 42
        AllTheAnswers._y = 43

        a = AllTheAnswers(400, 500)
        assert a.x == 42
        assert a.y == 43

        a.x = 401
        assert a.x == 401

        self.assertRaises(AttributeError, setattr, a, 'y', 501)

        assert AllTheAnswers.x == 42
        assert AllTheAnswers.y == 43



