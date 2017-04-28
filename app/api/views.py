# coding=utf-8
from flask import jsonify, request, g
from werkzeug.exceptions import NotFound

from . import api
from .custom_exceptions import ValidationException
from .decorators import token_required, catch_exceptions, admin_permission
from .errors import page_not_found, custom_error, bad_request
from .helpers import auth
from .utils import Utilities
from app.models import Url, ShortenUrl, AnonymousUser, ShortenUrlVisitLogs


@auth.login_required
@token_required
@catch_exceptions
def generate_shorten_url():
    """
    this function generates a shorten url and returns a response for an
    equivalent long url sent thorough a request dta body
    """
    try:
        Utilities.is_json(request)
        data = Utilities.get_json(request)
        Utilities.check_data_validity(data, ["url", "vanity_string",
                                             "shorten_url_length",
                                             "csrf_token", "submit"])
        Url.check_validity(data["url"])
        new_url, vanity_string, shorten_url_length = Url.get_from_json(data)
        Utilities.validate_vanity_string(vanity_string)
        if ShortenUrl.check_vanity_string_availability(vanity_string):
            return bad_request("The vanity string '{}' is already in "
                               "use. Please input another vanity string"
                               .format(vanity_string))
        AnonymousUser.set_anonymous()
        shorten_url = Url.get_shorten_url(new_url, vanity_string, shorten_url_length)
        return jsonify(
            message="Url successful shortened", shorten_url=shorten_url.to_dict()), 201
    except ValidationException as e:
        return e.broadcast()


@auth.login_required
@token_required
@admin_permission
@catch_exceptions
def get_urls():
    """Returns a list of all the long urls ordered by date of creation"""
    url_list = Url.get_all_urls_by_dated_added()
    return jsonify({"url_list": [url.to_dict()for url in url_list]})


@auth.login_required
@token_required
@catch_exceptions
def get_shorten_urls():
    """ returns a list of all the shorten urls ordered by date of creation """
    shorten_url_list = ShortenUrl.get_all_shorten_urls_by_dated_added()
    return jsonify(
        {
            "shorten_url_list": [
                shorten_url.to_dict() for shorten_url in shorten_url_list
            ]
        }
    )


@auth.login_required
@token_required
@catch_exceptions
def get_shorten_urls_by_popularity():
    """returns a list of all the shorten urls ordered by popularity"""
    shorten_url_list = ShortenUrl.get_all_shorten_urls_by_popularity()
    return jsonify(
        {
            "shorten_url_list": [
                shorten_url.to_dict() for shorten_url in shorten_url_list
            ]
        }
    )


@auth.login_required
@token_required
@catch_exceptions
def get_urls_for_particular_user():
    """Returns a list of all the long urls pertaining to a particular user"""
    AnonymousUser.set_anonymous()
    url_list = g.current_user.url_list
    return jsonify({"url_list": [url.to_dict() for url in url_list]})


@auth.login_required
@token_required
@catch_exceptions
def get_short_urls_for_particular_user():
    """
    returns a list of all the shorten urls pertaining to a
    particular user
    """
    AnonymousUser.set_anonymous()
    shorten_url_list = g.current_user.short_url_list
    return jsonify(
        {
            "shorten_url_list": [
                shorten_url.to_dict() for shorten_url in shorten_url_list
            ]
        }
    )


@auth.login_required
@token_required
@catch_exceptions
def get_total_shorten_urls_for_particular_user():
    """
    returns the total number of shorten urls a particular user
    have
    :return total: 
    """
    return jsonify(total_shorten_urls=len(list(g.current_user.short_url_list)))


@auth.login_required
@token_required
@catch_exceptions
def get_total_urls_for_particular_user():
    """
    returns the total number of long urls that a particular user
    have shortened
    :return total: 
    """
    return jsonify(total_urls=len(list(g.current_user.url_list)))


@catch_exceptions
def get_long_url_with_shorten_url_id(shorten_url_id):
    """
    returns a particular long url attached to a shorten url whose primary key
    is passed as argument
    """
    try:
        shorten_url_object = ShortenUrl.query.get_or_404(shorten_url_id)
        if shorten_url_object.deleted:
            return custom_error("The shorten url has been deleted", "deleted")
        elif not shorten_url_object.is_active:
            return custom_error("The shorten url has been deactivated",
                                "inactive")
        long_url = Url.query.get_or_404(shorten_url_object.long_url)
        update_visit_logs = ShortenUrlVisitLogs.create_visit_log_instance(
            id, request.remote_addr,request.environ["REMOTE_PORT"]
        )
        shorten_url_object.visits.append(update_visit_logs)
        return jsonify(long_url.to_dict())
    except NotFound:
        return page_not_found("Requested resource was not found")


@auth.login_required
@catch_exceptions
def get_long_url_with_shorten_url_name(shorten_url_name):
    """
    returns a particular long url attached to a shorten url whose name
    is passed as argument
    """
    try:
        shorten_url_object = ShortenUrl.query.filter_by(
            shorten_url_name=shorten_url_name).first_or_404()
        if shorten_url_object.deleted:
            return custom_error("The shorten url has been deleted", "deleted")
        elif not shorten_url_object.is_active:
            return custom_error("The shorten url has been deactivated",
                                "inactive")
        long_url = Url.query.get_or_404(shorten_url_object.long_url)
        visit_log = ShortenUrlVisitLogs\
            .create_visit_log_instance(shorten_url_object.id,
                                       request.environ["REMOTE_ADDR"],
                                       request.environ["REMOTE_PORT"])
        shorten_url_object.visits.append(visit_log)
        return jsonify(long_url.to_dict())
    except NotFound:
        return page_not_found("Requested resource was not found")


@auth.login_required
@token_required
@catch_exceptions
def update_shorten_url_long_url(shorten_url_id):
    """
    updates a particular long url attached to a shorten url whose primary key
    is passed as argument
    """
    try:
        Utilities.is_json(request)
        data = Utilities.get_json(request)
        Utilities.check_data_validity(data, ["url", "csrf_token", "submit"])
        Url.check_validity(data["url"])
        new_long_url = data["url"]
        shorten_url = ShortenUrl.query.get_or_404(shorten_url_id)
        shorten_url.confirm_user()
        shorten_url_target = Url.query.get_or_404(shorten_url.long_url)
        ShortenUrl.update_long_url(shorten_url, shorten_url_target,
                                   new_long_url)
        shorten_url = ShortenUrl.query.get_or_404(shorten_url_id)
        return jsonify(shorten_url.to_dict())
    except NotFound:
        return page_not_found("Requested resource was not found")
    except ValidationException as e:
        return e.broadcast()


@auth.login_required
@token_required
@catch_exceptions
def activate_shortened_url(shorten_url_id):
    """this function activates  a shorten_url"""
    try:
        shorten_url = ShortenUrl.query.get_or_404(shorten_url_id)
        shorten_url.confirm_user()
        return shorten_url.activate()
    except NotFound:
        return page_not_found("The shorten url you seek to "
                              "activate doesn't exist")


@auth.login_required
@token_required
@catch_exceptions
def deactivate_shortened_url(shorten_url_id):
    """this function deactivates  a shorten_url"""
    try:
        shorten_url = ShortenUrl.query.get_or_404(shorten_url_id)
        shorten_url.confirm_user()
        return shorten_url.deactivate()
    except NotFound:
        return page_not_found("The shorten url you seek to "
                              "deactivate doesn't exist")


@auth.login_required
@token_required
@catch_exceptions
def get_user_profile():
    """
    Queries the User model and fetches the user object whose primary key is 
    equivalent to the user_id passed in as argument
    :return User model instance: 
    """
    return jsonify(g.current_user.to_dict())


@auth.login_required
@token_required
@catch_exceptions
def delete_shortened_url(shorten_url_id):
    """this function deletes a shorten_url using its id"""
    try:
        shorten_url = ShortenUrl.query.get_or_404(shorten_url_id)
        shorten_url.confirm_user()
        response = shorten_url.delete()
        return response
    except NotFound:
        return page_not_found("The resource you seek to delete doesn't exist")


@auth.login_required
@token_required
@catch_exceptions
def restore_deleted_shortened_url(shorten_url_id):
    """this function reverts the deletion of a shorten_url using its id"""
    try:
        shorten_url = ShortenUrl.query.get_or_404(shorten_url_id)
        shorten_url.confirm_user()
        response = shorten_url.revert_delete()
        return response
    except NotFound:
        return page_not_found("The resource you seek to revert its deletion "
                              "doesn't exist")
