# coding=utf-8
from . import errors


class ValidationException(BaseException):
    def __init__(self, error_message):
        self.error = error_message

    def broadcast(self):
        return errors.validation_error(self.error)


class ServerException(BaseException):
    def __init__(self, error_message):
        self.error = error_message

    def broadcast(self):
        return errors.internal_server_error(self.error)


class UrlValidationException(BaseException):
    def __init__(self, error_message):
        self.error = error_message

    def broadcast(self):
        return errors.validation_error(self.error)
