import tempfile
import os
basedir = os.path.abspath(os.path.dirname(__file__))
db_file = tempfile.NamedTemporaryFile()


class Config(object):
    SECRET_KEY = 'secret key'
    IMAGE_FOLDER = os.path.join(basedir, os.pardir, "images")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IMAGE_NAME_LENGTH = 7
    IMAGES_PER_PAGE = 10


class ProdConfig(Config):
    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    S3_LOCATION = os.environ.get("S3_LOCATION")
    S3_KEY = os.environ.get("S3_KEY")
    S3_SECRET = os.environ.get("S3_SECRET")
    S3_UPLOAD_DIRECTORY = os.environ.get("S3_UPLOAD_DIRECTORY")
    S3_BUCKET = os.environ.get("S3_BUCKET")


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
