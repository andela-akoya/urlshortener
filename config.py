import dotenv
import os

dotenv.load()
# this variable gets this file directory path
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    This class is the base class for the different types of
    environment configuration
    """
    # gets the environment variable secret key or gives it a random value
    SECRET_KEY = dotenv.get('SECRET_KEY')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelopmentConfig(Config):
    """
    this is the development environment configuration, inheriting from the
    base configuration class and sets appropriate environment specific
    variables such as the database path and the debug value to True
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = dotenv.get('DEV_DATABASE_URL').format(basedir)


class TestingConfig(Config):
    """
    this is the testing environment configuration, inheriting from the
    base configuration class and sets appropriate environment specific
    variables such as the database path for testing and the testing
    variable value to True
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = dotenv.get('TEST_DATABASE_URL').format(basedir)


class ProductionConfig(Config):
    """
    this is the production environment configuration, inheriting from the
    base configuration class and sets appropriate environment specific
    variables such as the database path for production
    """
    SQLALCHEMY_DATABASE_URI = dotenv.get('DATABASE_URL').format(basedir)

# setting all the various environment configuration into the config dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
