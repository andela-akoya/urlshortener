from flask import g
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import import_string, cached_property

from . import api
from app.models import User, AnonymousUser


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    """
    this function verifies a username, password  orc token, and determines
    if a user is an authenticated user or an anonymous user
    """
    if username_or_token == "":
        g.current_user = AnonymousUser()
        g.token_sent = False
        return True
    if password == "":
        g.current_user = User.verify_auth_token(username_or_token)
        g.token_sent = True
        return g.current_user is not None
    user = User.get_by_username(username_or_token)
    g.token_sent = False
    if not user:
        return False
    g.current_user = user
    return user.verify_password(password)


def url(url_rules={}):
    for key, value in url_rules.items():
        api.add_url_rule(
            key,
            view_func=LazyView("app.api.{}".format(value["view"])),
            methods=value["methods"],
            strict_slashes=False
        )


class LazyView(object):

    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)

