# coding=utf-8
from flask import request, jsonify, g
from flask_httpauth import HTTPBasicAuth


from . import api, errors
from .custom_exceptions import ServerException, ValidationException
from .utilities import Utilities
from app.models import User, AnonymousUser

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    """
    this function verifies a username, password  or token, and determines
    if a user is an authenticated user or an anonymous user
    """
    if username_or_token == "":
        g.current_user = AnonymousUser()
        g.token_used = False
        return True
    if password == "":
        g.current_user = User.verify_auth_token(username_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.get_by_username(username_or_token)
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@api.route('/api/register', methods=['POST'], strict_slashes=False)
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
        Utilities.check_password_equality(data["password"],
                                          data["confirm_password"])
        User.save(User.get_from_json(data))
    except ValidationException as e:
        return e.broadcast()
    except Exception:
        return ServerException(
            "Registration failed due to an "
            "internal server error."
            "Please try again later")\
            .broadcast()

    return jsonify({"message": "Successfully Registered"}), 201


@api.route('/api/token/', strict_slashes=False)
@auth.login_required
def get_token():
    """authenticates a user and returns a token"""
    if g.current_user.is_anonymous or g.token_used:
        return errors.unauthorized()
    return jsonify({"message": "Authentication successful",
                    "token": g.current_user.generate_auth_token(3600),
                    "expiration": "3600 seconds"}), 200


@auth.error_handler
def auth_error():
    return errors.unauthorized("invalid credentials")
