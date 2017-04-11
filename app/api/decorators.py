# coding=utf-8
from functools import wraps
from flask import g
from .errors import forbidden, bad_request


def permission(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.current_user.is_anonymous:
            return forbidden("You are not authorized to use this service")
        return f(*args, **kwargs)
    return decorated_function


def admin_permission(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user.is_admin:
            return forbidden("You are not authorized to use this service")
        return f(*args, **kwargs)
    return decorated_function


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.token_used:
            return bad_request("Only token validation are acceptable")
        return f(*args, **kwargs)
    return decorated_function
