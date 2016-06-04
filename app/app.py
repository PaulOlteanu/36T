from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from random import randint
from PIL import Image
import os


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

    # Must be imported here instead of at the top to be able to call init_app after creating the app
    from .models import db, Photo
    db.init_app(app)

    # A basic route to test if the API is working
    @app.route("/")
    def index():
        return jsonify({
            "status": "Success",
            "message": "Welcome to the API!"
        })

    # Image uploading route
    # The input must be form encoded data, consisting of an image, and a title
    @app.route("/upload", methods=["POST"])
    def upload():

        # Make sure the file exists
        # The "key" for it must be "file", otherwise it will not be accepted
        if "file" not in request.files:
            return jsonify({
                "status": "Failure",
                "message": "File missing"
            })

        upload = request.files["file"]

        # Make sure the file extension is acceptable
        if upload.filename.split(".")[-1] not in ["png", "jpg", "bmp", "jpeg"]:
            return jsonify({
                "status": "Failure",
                "message": "Invalid file extension"
            })

        # Make sure a title is present
        if "title" not in request.form.keys():
            return jsonify({
                "status": "Failure",
                "message": "Title missing"
            })
        else:
            title = request.form["title"]

        # Open image for compressing
        image = Image.open(upload)

        # File to save the image to. The filename is randomly generated from the generateFilname function
        # Eventually this will have to check for a collision with an already existing filename
        new_filename = secure_filename(generateFilename(app.config["IMAGE_NAME_LENGTH"]) + "." + upload.filename.split(".")[-1])

        # The quality parameter compresses the image, saving space on the file system
        image.save(os.path.join(app.config["IMAGE_FOLDER"], new_filename), quality=40, optimize=True)

        image.close()

        # Create a database row for the image
        model = Photo(title=title, path=os.path.join(app.config["IMAGE_FOLDER"], secure_filename(new_filename)), votes=randint(0, 1000))
        db.session.add(model)
        db.session.commit()

        return jsonify({
            "status": "Success"
        })

    # Route to get all images sorted using reddit's hot algorithm
    @app.route("/hot")
    def hot():
        page = 1

        # Basic implementation of pagination
        # Defaults to page 1 if the page value isn't specified
        if ("page" in request.args.keys()):
            try:
                page = int(request.args["page"])
            except ValueError:
                return jsonify({
                    "status": "Failure",
                    "message": "Invalid page number"
                })

        # Implementation of reddit's hot sorting algorithm in SQL
        # This is implemented in SQL because it's sorting in the database and limiting to the number of images per page is more efficient than getting the whole table
        # The number of images per page is set in the config

        # Page has 1 subtracted from it because if not, it would be offset by IMAGES_PER_PAGE on the 1st page, and 2 * IMAGES_PER_PAGE on the 2nd one
        # The offset should actually be 0 for the first and IMAGES_PER_PAGE for the 2nd
        items = db.session.execute(
            "SELECT id, title, path, votes FROM photo ORDER BY LOG(ABS(votes) + 1) + (EXTRACT(EPOCH FROM created_on) / 300000) DESC OFFSET " +
            str(app.config["IMAGES_PER_PAGE"] * (page - 1)) + " LIMIT 20"
        )

        results = []

        # For now, this returns the image path instead of the image itself
        # This could be properly implemented in 2 ways: Either return all the images now, or just have a route to get an image by id and load them one at a time on the front end
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
