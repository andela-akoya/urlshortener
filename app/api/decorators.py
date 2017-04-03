# coding=utf-8
from functools import wraps
from flask import g
from .errors import forbidden


def permission(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.current_user.is_anonymous:
            return forbidden("You are not authorized to use this service")
        return f(*args, **kwargs)
    return decorated_function
