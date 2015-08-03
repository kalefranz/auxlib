# -*- coding: utf-8 -*-
import json
import logging
import sys

log = logging.getLogger(__name__)
root_log = logging.getLogger()

DEBUG_FORMATTER = logging.Formatter(
    "[%(levelname)s] [%(asctime)s.%(msecs)03d] %(process)d %(name)s:%(funcName)s(%(lineno)d):\n"
    "%(message)s\n",
    "%Y-%m-%d %H:%M:%S")

INFO_FORMATTER = logging.Formatter(
    "[%(levelname)s] [%(asctime)s.%(msecs)03d] %(process)d %(name)s(%(lineno)d): %(message)s\n",
    "%Y-%m-%d %H:%M:%S")


def set_root_level(level=logging.INFO):
    root_log.setLevel(level)


def attach_stderr(level=None):
    has_stderr_handler = any(handler.name == 'stderr' for handler in root_log.handlers)
    if not has_stderr_handler:
        handler = logging.StreamHandler(sys.stderr)
        handler.name = 'stderr'
        if level is not None:
            handler.setLevel(level)
        handler.setFormatter(DEBUG_FORMATTER if level == logging.DEBUG else INFO_FORMATTER)
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

    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(DEBUG_FORMATTER if level == logging.DEBUG else INFO_FORMATTER)
    rootlogger.addHandler(ch)


class DumpEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'dump'):
            return obj.dump()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
_DUMPS = DumpEncoder(indent=2, ensure_ascii=False, sort_keys=True).encode


def jsondumps(obj):
    return _DUMPS(obj)


def fullname(object):
    return object.__module__ + "." + object.__class__.__name__


def stringify(object):
    name = fullname(object)
    if name.startswith('bottle.'):
        builder = list()
        builder.append("{0} {1}{2} {3}".format(object.method,
                                               object.path,
                                               object.environ.get('QUERY_STRING', ''),
                                               object.get('SERVER_PROTOCOL')))
        builder += ["{0}: {1}".format(key, value) for key, value in object.headers.items()]
        builder.append('')
        body = object.body.read().strip()
        if body:
            builder.append(body)
            builder.append('')
        return "\n".join(builder)
    elif name == 'requests.PreparedRequest':
        builder = list()
        builder.append("{0} {1} {2}".format(object.method, object.path_url,
                                            object.url.split(':')[0]))
        builder += ["{0}: {1}".format(key, value) for key, value in object.headers().items()]
        builder.append('')
        if object.body:
            builder.append(object.body)
            builder.append('')
        return "\n".join(builder)


