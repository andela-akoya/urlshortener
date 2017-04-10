# coding=utf-8
from flask import jsonify, request, g
from werkzeug.exceptions import NotFound

from . import api
from .authentication import auth
from .custom_exceptions import ValidationException, UrlValidationException
from .decorators import permission, admin_permission
from .errors import page_not_found, custom_error
from .utilities import Utilities
from app.models import Url, ShortenUrl, AnonymousUser


@api.route('/api/url/shorten', methods=['POST'])
@auth.login_required
def generate_shorten_url():
    """
    this function generates a shorten url and returns a response for an
    equivalent long url sent thorough a request dta body
    """
    try:
        Utilities.is_json(request)
        data = Utilities.get_json(request)
        Utilities.check_data_validity(data, ["url", "vanity_string",
                                             "shorten_url_length"])
        Url.check_validity(data["url"])
        new_url, vanity_string, shorten_url_length = Url.get_from_json(data)
        ShortenUrl.check_vanity_string_availability(vanity_string)
        AnonymousUser.set_anonymous()
        shorten_url = Url.get_shorten_url(new_url, vanity_string,
                                          shorten_url_length)
        return jsonify(Utilities.to_json(shorten_url,
                                         ['id', 'shorten_url_name'])), 201
    except ValidationException as e:
        return e.broadcast()
    except UrlValidationException as e:
        return e.broadcast()


@api.route('/api/urls')
@api.route('/api/urls/popularity')
@auth.login_required
def get_urls():
    """ returns a list of all the long urls ordered by date of creation """
    url_list = Url.get_all_urls_by_dated_added()
    return jsonify(
        {
            "url_list": [
                Utilities.to_json(url, ['id', 'url_name', 'date_added'])
                for url in url_list
            ]
        }

    )


@api.route('/api/shorten-urls')
@api.route('/api/shorten-urls/popularity')
@auth.login_required
def get_shorten_urls():
    """ returns a list of all the shorten urls ordered by date of creation """
    shorten_url_list = ShortenUrl.get_all_shorten_urls_by_dated_added()
    return jsonify(
        {
            "shorten_url_list": [
                Utilities.to_json(shorten_url, ['id', 'url_name', 'date_added',
                                                'is_active', 'deleted'])
                for shorten_url in shorten_url_list
            ]
        }
    )


@api.route('/api/user/urls')
@auth.login_required
@permission
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
def get_urls_for_particular_user():
    """ returns a list of all the long urls pertaining to a particular user"""
    AnonymousUser.set_anonymous()
    url_list = g.current_user.url_list
    return jsonify(
        {
            "url_list": [
                Utilities.to_json(url, ['id', 'url_name']) for url in url_list
            ]
        }

    )


@api.route('/api/user/shorten-urls')
@auth.login_required
def get_short_urls_for_particular_user():
    """
    returns a list of all the shorten urls pertaining to a
    particular user
    """
    AnonymousUser.set_anonymous()
    short_url_list = g.current_user.short_url_list
    return jsonify(
        {
            "shorten_url_list": [
                Utilities.to_json(short_url, ['id', 'shorten_url_name',
                                              'date_added', 'is_active',
                                              'deleted'])
                for short_url in short_url_list
            ]
        }
    )


@api.route('/api/shorten-url/<int:id>/url')
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
        return jsonify(Utilities.to_json(long_url, ['id', 'url_name',
                                                    'date_added']))
    except NotFound:
        return page_not_found("Requested resource was not found")

@api.route('/api/shorten-url/<shorten_url_name>/url')
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
        return jsonify(Utilities.to_json(long_url, ['id', 'url_name',
                                                    'date_added']))
    except NotFound:
        return page_not_found("Requested resource was not found")

@api.route('/api/shorten-urls/<int:id>/url/update', methods=['PUT'])
@auth.login_required
@permission
def update_shorten_url_target(id):
    """
    updates a particular long url attached to a shorten url whose primary key
    is passed as argument
    """
    try:
        Utilities.is_json(request)
        data = Utilities.get_json(request)
        Utilities.check_data_validity(data, ["url"])
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

@api.route('/api/shorten-urls/<int:id>/activate', methods=['PUT'])
@api.route('/api/shorten-urls/<int:id>/deactivate', methods=['PUT'])
@auth.login_required
@permission
def activate_shorten_url(id):
    """this function activates or deactivates a shorten_url"""
    try:
        action_to_perform = request.path.split("/")[4]
        shorten_url = ShortenUrl.query.get_or_404(id)
        shorten_url.confirm_user()
        if action_to_perform == "activate":
            return shorten_url.activate()
        return shorten_url.deactivate()
    except NotFound:
        return page_not_found("The resource you seek to update doesn't exist")

@api.route('/api/shorten-urls/<shorten_url_name>/activate', methods=['PUT'])
@api.route('/api/shorten-urls/<shorten_url_name>/deactivate', methods=['PUT'])
@auth.login_required
@permission
def activate_shorten_url_with_name(shorten_url_name):
    """
    this function activates or deactivates a shorten_url based on the
    shorten_url name
    """
    try:
        action_to_perform = request.path.split("/")[4]
        shorten_url = ShortenUrl.query.filter_by(
            shorten_url_name=shorten_url_name).first_or_404()
        shorten_url.confirm_user()
        if action_to_perform == "activate":
            return shorten_url.activate()
        return shorten_url.deactivate()
    except NotFound:
        return page_not_found("The resource you seek to update doesn't exist")
