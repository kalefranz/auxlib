class NotFoundError(LookupError):
    pass


class InitializationError(EnvironmentError):
    pass


class SenderError(IOError):
    pass


class ValidationError(TypeError):

    def __init__(self, key, value=None, valid_types=None):
        if valid_types is None:
            if value is None:
                super(ValidationError, self).__init__("Missing or invalid parameter: "
                                                      "{}".format(key))
            else:
                super(ValidationError, self).__init__("Invalid value for {}: {}"
                                                      "".format(key, value))
        else:
            super(ValidationError, self).__init__("{0} must be of type {1}, not {2}"
                                                  "".format(key, valid_types, repr(value)))
