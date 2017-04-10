# coding=utf-8
from .custom_exceptions import ValidationException


class Utilities:
    """
    This class defines utility methods used for different purposes
    such as data integrity check, validation check
    """
    @staticmethod
    def is_json(request):
        """
        this function checks if a request is  json and also checks if the
        json data sent is not empty
        """
        if not request.is_json:
            raise ValidationException("Only json inputs are acceptable")
        elif len(request.data.decode('ascii')) == 0:
            raise ValidationException("Empty data are not acceptable")

    @staticmethod
    def get_json(request):
        """
        this function tries to extract data from the json request and raises
        an error if the data is not json serializable
        """
        try:
            data = request.json
        except Exception:
            raise ValidationException("The inputted data is not"
                                      " in json format")
        return data

    @staticmethod
    def check_data_validity(data, keys=[], exempt=False):
        """
        this function checks the data argument (dictionary) if it doesn't
        contain invalid keys and also if the valid keys have values.
        """
        invalid_keys = set(data.keys()).difference(keys)
        if invalid_keys and not exempt:
            raise ValidationException("The following {} are not valid keys"
                                      .format(invalid_keys))
        for key, values in data.items():
            if not (data[key]):
                raise ValidationException("{} can't be empty".format(key))

    @staticmethod
    def check_password_equality(password1, password2):
        """
        checks the equality of the passwords passed through the data and
        raises an error if the not equal
        """
        if password1 != password2:
            raise ValidationException("Passwords don't match")

    @staticmethod
    def to_json(data, keys):
        """converts dictionaries into its json equivalent"""
        data = data.__dict__
        for key in list(set(data.keys()).difference(keys)):
            del data[key]
        return data
