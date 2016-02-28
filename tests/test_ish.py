# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import logging

from auxlib.ish import dals

log = logging.getLogger(__name__)


def test_dals():
    test_string = """
        This little piggy went to the market.
        This little piggy stayed home.
        This little piggy had roast beef.
        """
    assert test_string.count('\n') == 4
    assert dals(test_string).count('\n') == 3


def test_dals_keep_space():
    test_string = """
        This little piggy went to the market.
          This little got indented."""
    assert test_string.count('\n') == 2
    assert dals(test_string).count('\n') == 1
    assert dals(test_string).count('  ') == 1
