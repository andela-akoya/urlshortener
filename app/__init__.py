from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from config import config


db = SQLAlchemy()  # instantiates the sqlalchemy database class
mail = Mail()  # instantiates the mail class
# instantiates the login manager
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "/login"


def create_app(config_name):
    """
    this function creates an application factory that creates the application
    instance using the configuration setting passed in as argument
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].__init__(app)

    # initializing app for the different packages
    db.init_app(app)  # initializes for database functionaries
    mail.init_app(app)  # initializes for mailing functionaries.
    login_manager.init_app(app)  # initializes for login management

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)  # registers api blueprint to app
    return app
