from .. import exceptions

class ConfigError(exceptions.BaseException):
    pass

class ConfigMismatch(ConfigError):
    pass

class EnsureMismatch(ConfigError):

    def __init__(self, object, attr, expected, real):
        super(EnsureMismatch, self).__init__("{!r}.{!r} value mismatch (required={!r}, existing={!r})".format(
            object, attr, expected, real,
        ))
        self.obj = object
        self.attr = attr
        self.expectedValue = expected
        self.realValue = real