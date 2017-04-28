# coding=utf-8
from flask import request, jsonify, g

from . import errors
from .custom_exceptions import ValidationException
from .decorators import catch_exceptions, token_required
from .helpers import auth
from .utils import Utilities
from app.models import User, Token


@catch_exceptions
def register():
    """this function registers a new user"""
    try:
        Utilities.is_json(request)
        data = Utilities.get_json(request)
        Utilities.check_data_validity(data,
                                      keys=["username", "password",
                                            "firstname", "lastname",
                                            "email", "confirm_password",
                                            "csrf_token", "submit"])
        User.check_username_uniqueness(data["username"])
        User.check_email_uniqueness(data["email"])
        new_user = User.save(User.convert_json_to_user_object(data))
    except ValidationException as e:
        return e.broadcast()

    return jsonify(
        {
            "message": "Successfully Registered",
            "user": new_user.to_dict()
        }
    ), 201


@auth.login_required
def get_token():
    """authenticates a user and returns a token"""
    if g.current_user.is_anonymous or g.token_sent:
        return errors.unauthorized()
    token = g.current_user.generate_auth_token(3600)
    return jsonify({"message": "Authentication successful",
                    "token": token,
                    }
                   ), 200


def has_token_expired(token):
    """
    checks if a token hasn't expired and returns true if token
    is still valid, otherwise it returns false
    :param token:
    :return boolean: 
    """
    return jsonify({"is_valid": bool(User.verify_auth_token(token))})


@auth.login_required
@token_required
def refresh_token():
    """
    this function refreshes an expired token. It also takes in the username and user_id
    to ensure authentication before refreshing the token
    :param username: 
    :param user_id: 
    :return string(token): 
    """
    Token.delete_expired_token()
    if g.current_user:
        token = g.current_user.generate_auth_token(3600)
        return jsonify({"message": "Token refresh successful",
                        "token": token,
                        }
                       ), 200


@auth.error_handler
def auth_error():
    return errors.unauthorized("invalid credentials")
