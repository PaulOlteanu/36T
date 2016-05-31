from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from random import randint
import os


def generateFilename(length):
    characters = list("01234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

    filename = ""

    for i in range(length):
        filename += characters[randint(0, len(characters))]

    return filename


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # This loads 36T/config.py as the default config
    # Then loads 36T/instance/config.py 2nd
    # Allows default settings in the 1st one and then further options based on the running environment
    app.config.from_object("config")
    app.config.from_pyfile("config.py")

    from .models import db, Photo
    db.init_app(app)

    @app.route("/")
    def index():
        return "Test"

    @app.route("/upload", methods=["POST"])
    def upload():

        if 'file' not in request.files:
            return jsonify({
                "status": "Failure",
                "message": "File missing"
            })

        upload = request.files["file"]

        if upload.filename.split(".")[-1] not in ["png", "jpg", "bmp", "jpeg"]:
            return jsonify({
                "status": "Failure",
                "message": "Invalid file extension"
            })

        if "title" not in request.form.keys():
            return jsonify({
                "status": "Failure",
                "message": "Title missing"
            })
        else:
            title = request.form["title"]

        new_filename = generateFilename(app.config["IMAGE_NAME_LENGTH"]) + "." + upload.filename.split(".")[-1]

        upload.save(os.path.join(app.config["IMAGE_FOLDER"], secure_filename(new_filename)))

        model = Photo(title=title, path=os.path.join(app.config["IMAGE_FOLDER"], secure_filename(new_filename)))
        db.session.add(model)
        db.session.commit()

        return jsonify({
            "status": "Success"
        })

    return app
