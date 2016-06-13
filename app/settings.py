import tempfile
import os
basedir = os.path.abspath(os.path.dirname(__file__))
db_file = tempfile.NamedTemporaryFile()


class Config(object):
    SECRET_KEY = 'secret key'
    IMAGE_FOLDER = os.path.join(basedir, os.pardir, "images")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IMAGE_NAME_LENGTH = 7
    IMAGES_PER_PAGE = 20


class ProdConfig(Config):
    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DB")


class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/Shamrok"

    ADMIN_PASSWORD = "Password"


class TestConfig(Config):
    ENV = 'test'
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/test"

    ADMIN_PASSWORD = "Password"

    IMAGE_FOLDER = IMAGE_FOLDER = os.path.join(basedir, os.pardir, "tests", "images")
