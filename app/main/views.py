# coding=utf-8
import json
from datetime import datetime

from flask import (current_app, redirect, render_template, request,
                   session, url_for)
from flask_login import login_required, logout_user, login_user, UserMixin

from . import main
from .forms import RegistrationForm, LoginForm
from app import login_manager


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


def update_context(data, context):
    """
    this function updates context dictionary
    with data passed in as argument.
    :param data:
    :param context:
    :return dict:
    """
    for key, value in data.items():
        context[key] = value
    return context


@login_manager.user_loader
def load_user(user_id):
    try:
        return User(session[user_id])
    except KeyError:
        return None


@main.route('/', strict_slashes=False)
@main.route('/index/', strict_slashes=False)
def index():
    if "user_id" in session:
        return redirect("/main/dashboard")
    return render_template("index/index.html")


@main.route("/homepage", strict_slashes=False)
@main.route('/register/', strict_slashes=False)
@main.route('/login/', strict_slashes=False)
def homepage():
    # renders the index page when any of the above route is reached
    if "user_id" in session:
        return redirect("/main/dashboard")
    register_form = RegistrationForm()
    login_form = LoginForm()
    context = {
        "title": "Nitly",
        "registerForm": register_form,
        "loginForm": login_form
    }
    return render_template("index/homepage.html", context=context)


@main.route('/start_session/', methods=["POST"], strict_slashes=False)
def login():
    data = request.json
    if "token" in data:
        user = User(data["id"])
        login_user(user, force=True)
        session[str(user.id)] = data
        return redirect("/main/dashboard")
    return redirect("/login")


@main.route('/main/<path:path>', methods=["GET", "POST"], strict_slashes=False)
@login_required
def main_route(path):
    context = session[session["user_id"]]
    context["title"] = "dashboard"
    context["path"] = path
    return render_template('content/main.html', context=context)


@main.route('/logout/', strict_slashes=False)
def logout():
    session.clear()
    logout_user()
    return redirect("/index")


@main.route('/credentials/', strict_slashes=False)
@login_required
def get_credentials():
    """
    this function returns the username and password of 
    the currently logged in user
    :return string: 
    """
    context = session[session["user_id"]]
    return json.dumps({"username": context["username"],
                       "id": context["id"]})


@main.route('/render_top_navigation/', methods=["POST"], strict_slashes=False)
@login_required
def render_navigation():
    """
    this function updates the navigation bar with
    necessary update passed through the request
    body
    :return string: 
    """
    data = request.json
    if isinstance(data, dict):
        context = update_context(data, session[session["user_id"]])
    return render_template("content/nav.html", context=context)


@main.route('/render_left_aside_navigation', methods=["POST"], strict_slashes=False)
@login_required
def render_left_aside_navigation():
    """
    this function updates the left aside navigation bar with
    necessary update passed through the request body
    :return string: 
    """
    data = request.json
    if isinstance(data, dict):
        context = update_context(data, session[session["user_id"]])
    return render_template("content/left_aside.html", context=context)


@main.route('/render_dashboard', methods=["POST"], strict_slashes=False)
@login_required
def render_dashboard():
    """
    this function updates the dashboard with
    necessary update passed through the request body
    :return string: 
    """
    data = request.json
    if isinstance(data, dict):
        context = update_context(data, session[session["user_id"]])
    return render_template("content/body_contents/dashboard.html", context=context)


@main.route('/render_shorten_url_content', methods=["POST"], strict_slashes=False)
@login_required
def render_shorten_url_page():
    """
    this function updates the shorten url page with
    necessary update passed through the request body
    :return string: 
    """
    data = request.json
    if isinstance(data, dict):
        context = update_context(data, session[session["user_id"]])
    return render_template("content/body_contents/shorten_url.html", context=context)
