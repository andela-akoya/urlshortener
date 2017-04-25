# coding=utf-8
from flask import jsonify, request, g
from werkzeug.exceptions import NotFound

from . import api
from .authentication import auth
from .custom_exceptions import ValidationException, UrlValidationException
from .decorators import token_required, catch_exceptions, admin_permission
from .errors import page_not_found, custom_error
from .utilities import Utilities
from app.models import Url, ShortenUrl, AnonymousUser, ShortenUrlVisitLogs


@api.route('/url/shorten/', methods=['POST'], strict_slashes=False)
@auth.login_required
@token_required
# @catch_exceptions
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
        ShortenUrl.check_vanity_string_availability(vanity_string)
        AnonymousUser.set_anonymous()
        output = Url.get_shorten_url(new_url, vanity_string,
                                          shorten_url_length)
        shorten_url = Utilities.to_json(output[1], ['id', 'shorten_url_name'])
        shorten_url["shorten_url_name"] = request.url_root + shorten_url["shorten_url_name"]
        return jsonify(message=output[0],shorten_url=shorten_url), 201
    except ValidationException as e:
        return e.broadcast()
    except UrlValidationException as e:
        return e.broadcast()


@api.route('/urls/', strict_slashes=False)
@auth.login_required
@token_required
@admin_permission
@catch_exceptions
def get_urls():
    """Returns a list of all the long urls ordered by date of creation"""
    url_list = Url.get_all_urls_by_dated_added()
    return jsonify(
        {
            "url_list": [
                Utilities.to_json(url, ['id', 'url_name', 'date_added'])
                for url in url_list
            ]
        }

    )


@api.route('/shorten-urls/', strict_slashes=False)
@api.route('/shorten-urls/popularity/', strict_slashes=False)
@auth.login_required
@token_required
@catch_exceptions
def get_shorten_urls():
    """ 
    returns a list of all the shorten urls ordered by date of creation 
    or popularity based on the endpoint reached
    """
    shorten_url_list = ShortenUrl.get_all_shorten_urls_by_dated_added()
    if "popularity" in request.url:
        shorten_url_list = ShortenUrl.get_all_shorten_urls_by_popularity()
    return jsonify(
        {
            "shorten_url_list": [
                shorten_url.to_json() for shorten_url in shorten_url_list
            ]
        }
    )


@api.route('/user/urls/', strict_slashes=False)
@auth.login_required
def get_urls():
    """ returns a list of all the long urls ordered by date of creation """
    url_list = Url.query.order_by(desc(Url.date_added)).all()
    return jsonify(
        [Utilities.to_json(url, ['id', 'url_name', 'date_added']) for url in url_list]
    )

@api.route('/api/shorten-urls')
@auth.login_required
@permission
def get_shorten_urls():
    """ returns a list of all the shorten urls ordered by date of creation """
    shorten_url_list = ShortenUrl.query.order_by(desc(ShortenUrl.date_added)).all()
    return jsonify([Utilities.to_json(
        shorten_url, ['id', 'url_name', 'date_added'])
                    for shorten_url in shorten_url_list]
    )


@api.route('/api/user/urls')
@auth.login_required
@token_required
@catch_exceptions
def get_urls_for_particular_user():
    """Returns a list of all the long urls pertaining to a particular user"""
    AnonymousUser.set_anonymous()
    url_list = g.current_user.url_list
    return jsonify(
        {
            "url_list": [
                Utilities.to_json(url, ['id', 'url_name', 'date_added']) for url in url_list
            ]
        }

    )


@api.route('/user/shorten-urls/', strict_slashes=False)
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
                shorten_url.to_json() for shorten_url in shorten_url_list
            ]
        }
    )


@api.route('/user/shorten-urls/total/', strict_slashes=False)
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


@api.route('/user/urls/total/', strict_slashes=False)
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


@api.route('/shorten-url/<int:id>/url/', strict_slashes=False)
@catch_exceptions
def get_long_url_with_shorten_url_id(id):
    """
    returns a particular long url attached to a shorten url whose primary key
    is passed as argument
    """
    try:
        shorten_url_object = ShortenUrl.query.get_or_404(id)
        if shorten_url_object.deleted:
            return custom_error("The shorten url has been deleted", "deleted")
        elif not shorten_url_object.is_active:
            return custom_error("The shorten url has been deactivated",
                                "inactive")
        long_url = Url.query.get_or_404(shorten_url_object.long_url)
        visit_log = ShortenUrlVisitLogs.create_visit_log_instance(id, request.remote_addr,
                                                      request.environ["REMOTE_PORT"])
        shorten_url_object.visits.append(visit_log)
        return jsonify(Utilities.to_json(long_url, ['id', 'url_name',
                                                    'date_added']))
    except NotFound:
        return page_not_found("Requested resource was not found")

@api.route('/shorten-url/<shorten_url_name>/url/', strict_slashes=False)
@auth.login_required
@catch_exceptions
def get_long_url_with_shorten__url_name(shorten_url_name):
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
        visit_log = ShortenUrlVisitLogs.create_visit_log_instance(shorten_url_object.id, request.environ["REMOTE_ADDR"], request.environ["REMOTE_PORT"])
        shorten_url_object.visits.append(visit_log)
        return jsonify(Utilities.to_json(long_url, ['id', 'url_name',
                                                    'date_added']))
    except NotFound:
        return page_not_found("Requested resource was not found")

@api.route('/shorten-urls/<int:id>/url/update/', methods=['PUT'], strict_slashes=False)
@auth.login_required
@token_required
@catch_exceptions
def update_shorten_url_target(id):
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
        shorten_url = ShortenUrl.query.get_or_404(id)
        shorten_url.confirm_user()
        shorten_url_target = Url.query.get_or_404(shorten_url.long_url)
        ShortenUrl.update_target_url(shorten_url, shorten_url_target,
                                     new_long_url)
        shorten_url = ShortenUrl.query.get_or_404(id)
        return jsonify({
            "id": shorten_url.id,
            "shorten_url_name": shorten_url.shorten_url_name,
            "date_added": shorten_url.date_added,
            "long_url": Url.query.get(shorten_url.long_url).url_name
        })
    except NotFound:
        return page_not_found("Requested resource was not found")
    except ValidationException as e:
        return e.broadcast()
    except UrlValidationException as e:
        return e.broadcast()

@api.route('/shorten-urls/<int:id>/activate/', methods=['PUT'], strict_slashes=False)
@api.route('/shorten-urls/<int:id>/deactivate/', methods=['PUT'], strict_slashes=False)
@auth.login_required
@token_required
@catch_exceptions
def activate_shorten_url(id):
    """this function activates or deactivates a shorten_url"""
    action_to_perform = request.path.split("/")[5]
    try:
        shorten_url = ShortenUrl.query.get_or_404(id)
        shorten_url.confirm_user()
        if action_to_perform == "activate":
            return shorten_url.activate()
        return shorten_url.deactivate()
    except NotFound:
        return page_not_found("The resource you seek to {} doesn't exist"
                              .format(action_to_perform))

@api.route('/shorten-urls/<shorten_url_name>/activate/', methods=['PUT'], strict_slashes=False)
@api.route('/shorten-urls/<shorten_url_name>/deactivate/', methods=['PUT'], strict_slashes=False)
@auth.login_required
@token_required
@catch_exceptions
def activate_shorten_url_with_name(shorten_url_name):
    """
    this function activates or deactivates a shorten_url based on the
    shorten_url name
    """
    action_to_perform = request.path.split("/")[5]
    try:
        shorten_url = ShortenUrl.query.filter_by(
            shorten_url_name=shorten_url_name).first_or_404()
        shorten_url.confirm_user()
        if action_to_perform == "activate":
            return shorten_url.activate()
        return shorten_url.deactivate()
    except NotFound:
        return page_not_found("The resource you seek to {} doesn't exist"
                              .format(action_to_perform))


@api.route('/user/profile', strict_slashes=False)
@auth.login_required
@token_required
@catch_exceptions
def get_user_data():
    """
    Queries the User model and fetches the user object whose primary key is 
    equivalent to the user_id passed in as argument
    :return User model instance: 
    """
    return jsonify(Utilities.to_json(g.current_user, ["username", "email",
                                                      "firstname", "lastname",
                                                      "date_added", "id"]))


@api.route('/shorten-urls/<int:id>/delete/', methods=['DELETE'], strict_slashes=False)
@auth.login_required
@token_required
@catch_exceptions
def delete_shorten_url(id):
    """this function deletes a shorten_url using its id"""
    try:
        shorten_url = ShortenUrl.query.get_or_404(id)
        shorten_url.confirm_user()
        return shorten_url.delete()
    except NotFound:
        return page_not_found("The resource you seek to delete doesn't exist")


@api.route('/shorten-urls/<int:id>/restore/', methods=['PUT'], strict_slashes=False)
@auth.login_required
@token_required
@catch_exceptions
def revert_delete_shorten_url(id):
    """this function reverts the deletion of a shorten_url using its id"""
    try:
        shorten_url = ShortenUrl.query.get_or_404(id)
        shorten_url.confirm_user()
        return shorten_url.revert_delete()
    except NotFound:
        return page_not_found("The resource you seek to revert its deletion "
                              "doesn't exist")
