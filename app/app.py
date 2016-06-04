from flask import Flask, request, jsonify, Response
from werkzeug.utils import secure_filename

from datetime import datetime, timedelta
from random import randint
from PIL import Image
from math import log
import os
import json


def generateFilename(length):
    characters = list("01234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

    filename = ""

    for i in range(length):
        filename += characters[randint(0, len(characters) - 1)]

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

        if "file" not in request.files:
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

        new_filename = secure_filename(generateFilename(app.config["IMAGE_NAME_LENGTH"]) + "." + upload.filename.split(".")[-1])

        upload.save(os.path.join(app.config["IMAGE_FOLDER"], new_filename))

        image = Image.open(os.path.join(app.config["IMAGE_FOLDER"], new_filename))

        image.save(os.path.join(app.config["IMAGE_FOLDER"], new_filename), quality=25, optimize=True)

        image.close()

        model = Photo(title=title, path=os.path.join(app.config["IMAGE_FOLDER"], secure_filename(new_filename)), votes=randint(0, 1000))
        db.session.add(model)
        db.session.commit()

        return jsonify({
            "status": "Success"
        })

    @app.route("/hot")
    def hot():
        page = 1

        if ("page" in request.args.keys()):
            try:
                page = int(request.args["page"])
            except ValueError:
                return jsonify({
                    "status": "Failure",
                    "message": "Invalid page number"
                })

        items = db.session.execute("SELECT id, title, path, votes FROM photo ORDER BY LOG(ABS(votes) + 1) + (EXTRACT(EPOCH FROM created_on) / 300000) DESC OFFSET " + str(20 * (page - 1)) + " LIMIT 20")

        results = []

        for row in items:
            results.append({
                "id": row.id,
                "title": row.title,
                "path": row.path,
                "votes": row.votes
            })

        return jsonify({
            "status": "Success",
            "data": results
        })

    return app
