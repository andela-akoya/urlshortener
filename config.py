import os

# this variable gets this file directory path
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    This class is the base class for the different types of
    environment configuration
    """
    # gets the environment variable secret key or gives it a default value
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def __init__(app):
        # instantiates the app based on the configuration of the environment
        pass


class DevelopmentConfig(Config):
    """
    this is the development environment configuration, inheriting from the
    base configuration class and sets appropriate environment specific
    variables such as the database path and the debug value to True
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')



class TestingConfig(Config):
    """
    this is the testing environment configuration, inheriting from the
    base configuration class and sets appropriate environment specific
    variables such as the database path for testing and the testing
    variable value to True
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    """
    this is the production environment configuration, inheriting from the
    base configuration class and sets appropriate environment specific
    variables such as the database path for production
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

# setting all the various environment configuration into the config dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
