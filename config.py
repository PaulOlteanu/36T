import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, "db_repository")
SQLALCHEMY_TRACK_MODIFICATIONS = False

IMAGE_FOLDER = os.path.join(basedir, "images")
