import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "postgresql://localhost/36T"
SQLALCHEMY_TRACK_MODIFICATIONS = False

IMAGE_FOLDER = os.path.join(basedir, "images")

IMAGE_NAME_LENGTH = 7
