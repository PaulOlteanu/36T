import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

IMAGE_FOLDER = os.path.join(basedir, "images")

IMAGE_NAME_LENGTH = 7
