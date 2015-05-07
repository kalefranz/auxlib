# -*- coding: utf-8 -*-
import logging
import sys


log = logging.getLogger(__name__)
root_log = logging.getLogger()


def set_root_level(level=logging.DEBUG):
    root_log.setLevel(level)


def attach_stderr(level=None):
    # TODO: set root log level if not set already
    has_stderr_handler = any(handler.name == 'stderr' for handler in root_log.handlers)
    if not has_stderr_handler:
        handler = logging.StreamHandler(sys.stderr)
        handler.name = 'stderr'
        if level is not None:
            handler.setLevel(level)
        root_log.addHandler(handler)
        return True
    else:
        return False


def detach_stderr():
    for handler in root_log.handlers:
        if handler.name == 'stderr':
            root_log.removeHandler(handler)
            return True
    return False
