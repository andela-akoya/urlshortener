# coding=utf-8
from flask import g, jsonify

from . import api


def process_response(status_code, data):
    """
    this function processes any request and returns the appropriate
    content type based on the mime-type set in the request header.
    """
    response = jsonify(data)
    response.status_code = status_code
    if status_code == 401:
        response.headers['WWW-Authenticate'] = "Unauthorized"
    return response


@api.app_errorhandler(404)
def page_not_found(e):
    """Returns  404 status code if resource isn't available"""
    context = {'error': 'Not found', 'message': str(e)}
    return process_response(404, context)


@api.app_errorhandler(500)
def internal_server_error(e):
    """Returns a 500 status code for an internal server error"""
    context = {'error': 'internal server error', 'message': str(e)}
    return process_response(500, context)


@api.app_errorhandler(403)
def forbidden(e):
    """Returns a 403 status code for forbidden access"""
    context = {"error": 'forbidden', 'message': str(e)}
    return process_response(403, context)


@api.app_errorhandler(400)
def bad_request(e="Invalid credentials"):
    """Returns a 400 status code for bad request"""
    context = {'error': 'bad request', 'message': str(e)}
    return process_response(400, context)


@api.app_errorhandler(401)
def unauthorized(e="Invalid Credentials"):
    """Returns a 401 status code for unauthorized access"""
    if g.token_sent:
        e = "Token has expired"
    context = {'error': 'unauthorized', 'message': str(e)}
    return process_response(401, context)


@api.errorhandler(400)
def validation_error(e):
    """Returns a 400 status code for data validation failure"""
    context = {'error': 'validation error', 'message': str(e)}
    return process_response(400, context)


@api.app_errorhandler(405)
def method_not_allowed(e):
    """Returns a 405 status code for wrong method"""
    context = {'error': str(e).split(":")[0], 'message': str(e).split(":")[1]}
    return process_response(405, context)


@api.errorhandler(400)
def custom_error(message, status):
    """Returns a custom defined error for a deleted and inactive shorten urls"""
    context = {"error": "bad request", "message": message, "status": status}
    return process_response(400, context)
