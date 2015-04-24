# -*- coding: utf-8 -*-
import logging
import sys


def set_app_to_stderr(level=logging.INFO):
    """Calling this function will make all logs above the given level write to STDERR."""
    log = logging.getLogger()
    log.setLevel(level)
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(level)
    log.addHandler(ch)
