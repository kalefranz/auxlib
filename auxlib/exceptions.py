from enum import Enum


def Raise(exception):
    raise exception


class AuxlibError(object):
    """Mixin to identify all exceptions associated with the auxlib package."""


class NotFoundError(AuxlibError, KeyError):
    pass


class InitializationError(AuxlibError, EnvironmentError):
    pass


class SenderError(AuxlibError, IOError):
    pass


class AssignmentError(AuxlibError, AttributeError):
    pass


class ValidationError(AuxlibError, TypeError):

    def __init__(self, key, value=None, valid_types=None, msg=None):
        if msg is not None:
            super(ValidationError, self).__init__(msg)
        elif valid_types is None:
            super(ValidationError, self).__init__("Invalid value {} for {}"
                                                  "".format(value, key))
        else:
            super(ValidationError, self).__init__("{0} must be of type {1}, not {2}"
                                                  "".format(key, valid_types, repr(value)))
