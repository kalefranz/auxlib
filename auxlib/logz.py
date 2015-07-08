# -*- coding: utf-8 -*-
import json
import logging
import sys


log = logging.getLogger(__name__)
root_log = logging.getLogger()


TWO_LINE_FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - '
                                       '%(funcName)s:%(lineno)d\n'
                                       '%(message)s')


def set_root_level(level=logging.INFO):
    root_log.setLevel(level)


def attach_stderr(level=None):
    has_stderr_handler = any(handler.name == 'stderr' for handler in root_log.handlers)
    if not has_stderr_handler:
        handler = logging.StreamHandler(sys.stderr)
        handler.name = 'stderr'
        if level is not None:
            handler.setLevel(level)
        handler.setFormatter(TWO_LINE_FORMATTER)
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


def initialize_logging(level=logging.INFO):
    rootlogger = logging.getLogger()
    rootlogger.setLevel(level)
    applogger = logging.getLogger(APP_NAME)
    applogger.setLevel(logging.DEBUG)
    applogger.propagate = False

    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(formatter)
    rootlogger.addHandler(ch)
    applogger.addHandler(ch)


class DumpEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'dump'):
            return obj.dump()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
_DUMPS = DumpEncoder(indent=2, ensure_ascii=False, sort_keys=True).encode


def jsondumps(obj):
    return _DUMPS(obj)
