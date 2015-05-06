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

    def __init__(self, key, value=None, valid_types=None):
        if valid_types is None:
            if value is None:
                super(ValidationError, self).__init__("Missing or invalid parameter: "
                                                      "{}".format(key))
            else:
                super(ValidationError, self).__init__("Invalid value for {}: {}"
                                                      "".format(key, value))
        else:
            if isinstance(valid_types, Enum):
                super(ValidationError, self).__init__("Cannot set {0}. {1} is not a "
                                                      "valid {2}."
                                                      "".format(key, repr(value), valid_types))
            else:
                super(ValidationError, self).__init__("{0} must be of type {1}, not {2}"
                                                      "".format(key, valid_types, repr(value)))
