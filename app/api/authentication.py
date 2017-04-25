# coding=utf-8
from time import localtime, strftime

from flask import request, jsonify, g
from flask_httpauth import HTTPBasicAuth

from . import api, errors
from .custom_exceptions import ServerException, ValidationException
from.decorators import catch_exceptions
from .utilities import Utilities
from app.models import User, AnonymousUser, Token

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
        g.token = username_or_token
        return g.current_user is not None
    user = User.get_by_username(username_or_token)
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@api.route('/register', methods=['POST'], strict_slashes=False)
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
        Utilities.check_password_equality(data["password"],
                                          data["confirm_password"])
        User.save(User.get_from_json(data))
    except ValidationException as e:
        return e.broadcast()

    return jsonify({"message": "Successfully Registered"}), 201


@api.route('/token/', strict_slashes=False)
@auth.login_required
def get_token():
    """authenticates a user and returns a token"""
    if g.current_user.is_anonymous or g.token_used:
        return errors.unauthorized()
    token_generated = Token.check_existence_of_valid_token(g.current_user.id)
    if not token_generated:
        token_generated = g.current_user.generate_auth_token(3600)
        Token.save(token_generated)
    return jsonify({"message": "Authentication successful",
                    "token": token_generated[1],
                    "time generated": strftime("%a, %d %b %Y %I:%M:%S %p ",
                                               localtime(token_generated[0])),
                    "time generated in seconds": token_generated[0],
                    "expiration time": strftime("%a, %d %b %Y %I:%M:%S %p",
                                                localtime(token_generated[0] + 3600)),
                    "expiration time in seconds": token_generated[0] + 3600}), 200


@api.route('/token/<token>/validity/', strict_slashes=False)
def check_token_validity(token):
    """
    checks if a token hasn't expired and returns true if token
    is still valid, otherwise it returns false
    :param token:
    :return boolean: 
    """
    return jsonify({"is_valid": bool(User.verify_auth_token(token))})


@api.route('/<username>/<int:user_id>/token/refresh/', strict_slashes=False)
def refresh_token(username, user_id):
    """
    this function refreshes an expired token. It also takes in the username and user_id
    to ensure authentication before refreshing the token
    :param username: 
    :param user_id: 
    :return string(token): 
    """
    Token.delete_expired_token()
    g.current_user = User.query.filter_by(username=username, id=user_id).first()
    if g.current_user:
        token_generated = g.current_user.generate_auth_token(3600)
        Token.save(token_generated)
        return jsonify({"message": "Token refresh successful",
                        "token": token_generated[1],
                        "time generated": strftime(
                            "%a, %d %b %Y %I:%M:%S %p ",
                            localtime(token_generated[0])),
                        "time generated in seconds": token_generated[0],
                        "expiration time": strftime(
                            "%a, %d %b %Y %I:%M:%S %p",
                            localtime(token_generated[0] + 3600)),
                        "expiration time in seconds": token_generated[
                                                          0] + 3600}), 200


@auth.error_handler
def auth_error():
    return errors.unauthorized("invalid credentials")
