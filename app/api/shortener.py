# coding=utf-8
import string
import uuid
from random import SystemRandom


class Shortener:
    @staticmethod
    def generate_short_name(length_of_short_url):
        """
        generates a  random string having a length equal to the integer
        argument (length_of_short_url parameter)
        """

        short_url_length = length_of_short_url or 6
        characters = "{upper_case_string}{digits}{lower_case_string}{unique_id}".format(
            upper_case_string=string.ascii_uppercase,
            digits=string.digits,
            lower_case_string=string.ascii_lowercase,
            unique_id=str(uuid.uuid4()).replace("-", "")
        )
        return ''.join(SystemRandom().choice(characters)
                       for _ in range(short_url_length))
