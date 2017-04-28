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
            raise ValidationException("Empty data is not acceptable")

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
    def check_data_validity(data, keys=None):
        """
        this function checks the data argument (dictionary) if it doesn't
        contain invalid keys and also if the valid keys have values.
        """
        keys = keys if keys else []
        invalid_keys = set(data.keys()).difference(keys)
        if invalid_keys:
            raise ValidationException("The following {} are not valid keys"
                                      .format(invalid_keys))
        for key, values in data.items():
            if not (data[key]):
                raise ValidationException("{} can't be empty".format(key))
        if "password" in data:
            Utilities.check_password_equality(data["password"],
                                              data["confirm_password"])

    @staticmethod
    def check_password_equality(password1, password2):
        """
        checks if password1 equals to password2 and
        raises an error if they are  not equal
        """
        if password1 != password2:
            raise ValidationException("Passwords don't match")

    @staticmethod
    def validate_vanity_string(vanity_string):
        """
        checks if the vanity string contains spaces
        and returns appropriate error response if it does
        """
        if vanity_string and " " in vanity_string:
            raise ValidationException("Vanity string cannot contain spaces")
