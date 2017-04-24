# coding=utf-8
from functools import wraps

from flask import g

from .custom_exceptions import ServerException
from .errors import forbidden, bad_request


def permission(f):
    """
    checks the permission of the current user  trying to access an
    endpoint resource if its not anonymous and flags an error if 
    the user is anonymous
    :param f:  
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.current_user.is_anonymous:
            return forbidden("You are not authorized to use this service")
        return f(*args, **kwargs)
    return decorated_function


def admin_permission(f):
    """
    checks for admin permission when a user tries to access an endpoint
    decorated with it and flags an error message if the user fails
    the validation
    :param f: 
    :return: 
    """
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
            return bad_request("Only token validation is acceptable")
        return f(*args, **kwargs)
    return decorated_function


def catch_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            res = f(*args, **kwargs)
        except Exception:
            return ServerException("Something went wrong. "
                                   "We will work on fixing "
                                   "that right away.").broadcast()
        return res
    return decorated_function
