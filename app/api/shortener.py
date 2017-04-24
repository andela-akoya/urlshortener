# coding=utf-8
import string
import uuid
from random import SystemRandom


class Shortener:
    @staticmethod
    def generate_shorten_name(length_of_short_url):
        """
        generates a  random string having a length equal to the integer
        argument (length_of_short_url parameter)
        """

        short_url_length = length_of_short_url if length_of_short_url else 6
        characters = string.ascii_uppercase + string.digits \
                     + string.ascii_lowercase \
                     + str(uuid.uuid4()).replace("-", "")

        return ''.join(SystemRandom().choice(characters)
                       for _ in range(short_url_length))
