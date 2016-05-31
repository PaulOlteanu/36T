from flask import Flask, request, redirect, jsonify
from baseconv import BaseConverter
from werkzeug.utils import secure_filename
from flask.ext.sqlalchemy import SQLAlchemy
import os

app = Flask(__name__, instance_relative_config=True)
db = SQLAlchemy(app)

from .models import Photo

# This loads 36T/config.py as the default config
# Then loads 36T/instance/config.py 2nd
# Allows default settings in the 1st one and then further options based on the running environment
app.config.from_object("config")
app.config.from_pyfile("config.py")

base62 = BaseConverter("1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
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

    new_filename = base62.encode(app.config["FILE_NUMBER"]) + "." + upload.filename.split(".")[-1]
    app.config["FILE_NUMBER"] = app.config["FILE_NUMBER"] + 1

    upload.save(os.path.join(app.config["IMAGE_FOLDER"], secure_filename(new_filename)))

    model = Photo(title=title, path=os.path.join(app.config["IMAGE_FOLDER"], secure_filename(new_filename)))
    db.session.add(model)
    db.session.commit()

    return jsonify({
        "status": "Success"
    })
