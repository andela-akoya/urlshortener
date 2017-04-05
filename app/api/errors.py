# coding=utf-8
from flask import jsonify

from . import api


def process_request(status_code, data):
    """
    this function processes any request and returns the appropriate
    content type based on the mime-type set in the request header.
    """
    response = jsonify(data)
    response.status_code = status_code
    return response


@api.app_errorhandler(404)
def page_not_found(e):
    # returns  404 status code if resource isn't available
    context = {'error': 'Not found', 'message': str(e)}
    return process_request(404, context)


@api.app_errorhandler(500)
def internal_server_error(e):
    # returns a 500 status code for an internal server error
    context = {'error': 'internal server error', 'message': str(e)}
    return process_request(500, context)


@api.app_errorhandler(403)
def forbidden(e):
    # returns a 403 status code for forbidden access
    context = {"error": 'forbidden', 'message': str(e)}
    return process_request(403, context)


# @auth.error_handler
@api.app_errorhandler(400)
def bad_request(e="Invalid credentials"):
    # returns a 400 status code for bad request
    context = {'error': 'bad request', 'message': str(e)}
    return process_request(400, context)


@api.app_errorhandler(401)
def unauthorized(e="Invalid Credentials"):
    # returns a 401 status code for unauthorized access
    context = {'error': 'unauthorized', 'message': str(e)}
    return process_request(401, context)


@api.errorhandler(400)
def validation_error(e):
    # returns a 400 status code for data validation failure
    context = {'error': 'validation error', 'message': str(e)}
    return process_request(400, context)


@api.app_errorhandler(405)
def method_not_allowed(e):
    # returns a 405 status code for wrong method
    context = {'error': str(e).split(":")[0], 'message': str(e).split(":")[1]}
    return process_request(405, context)






