import tempfile
import os
basedir = os.path.abspath(os.path.dirname(__file__))
db_file = tempfile.NamedTemporaryFile()


class Config(object):
    SECRET_KEY = 'secret key'
    IMAGE_FOLDER = os.path.join(basedir, "..", "images")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IMAGE_NAME_LENGTH = 7
    IMAGES_PER_PAGE = 20


class ProdConfig(Config):
    ENV = 'prod'
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/36T"


class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/36T"

    ADMIN_PASSWORD = "Password"


class TestConfig(Config):
    ENV = 'test'
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/test"
    SQLALCHEMY_ECHO = True

    ADMIN_PASSWORD = "Password"
