#! ../env/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Paul Olteanu'
__email__ = 'p.a.olteanu@gmail.com'
__version__ = '1.0'

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from random import randint
from PIL import Image
import os

from .models import db, Photo


def generateFilename(length):
    characters = list("01234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

    filename = ""

    for i in range(length):
        filename += characters[randint(0, len(characters) - 1)]

    return filename


def create_app(object_name):
    """
    An flask application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object, e.g. threesixty.settings.ProdConfig
    """

    app = Flask(__name__)

    app.config.from_object(object_name)

    # initialize SQLAlchemy
    db.init_app(app)

    # A basic route to test if the API is working
    @app.route("/")
    def index():
        return jsonify({
            "status": "Success",
            "message": "Welcome to the API!"
        })

    # Images route. Allows users to get all images, or to upload an image
    @app.route("/images", methods=["GET", "POST"])
    def images():

        # GET route. Returns all images, in order of id, which is also in order of oldest -> newest
        if request.method == "GET":

            images = Photo.query.all()

            results = []

            for row in images:
                results.append({
                    "id": row.id,
                    "title": row.title,
                    "path": row.path,
                    "votes": row.votes,
                    "creation_date": row.created_on
                })

            return jsonify({
                "status": "Success",
                "data": results
            })

        # POST route. Images are uploaded here
        # The input must be form encoded data, consisting of an image, and a title
        elif request.method == "POST":

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
            # TODO: Remove the random votes number, and also the argument from the model constructor. This is only there for ease of development
            model = Photo(title=title, path=os.path.join(app.config["IMAGE_FOLDER"], secure_filename(new_filename)), votes=randint(0, 1000))
            db.session.add(model)
            db.session.commit()

            return jsonify({
                "status": "Success"
            })

    @app.route("/images/new")
    def new():
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

        images = Photo.query.order_by(Photo.created_on.desc()).offset(app.config["IMAGES_PER_PAGE"] * (page - 1)).limit(app.config["IMAGES_PER_PAGE"])

        results = []

        for row in images:
            results.append({
                "id": row.id,
                "title": row.title,
                "path": row.path,
                "votes": row.votes,
                "creation_date": row.created_on
            })

        return jsonify({
            "status": "Success",
            "data": results
        })

    # Route to get all images sorted using reddit's hot algorithm
    @app.route("/images/hot")
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

        # 45000 is a magic number in reddit's code too. It's the number of seconds in 12.5 hours
        # The way the algorithm works requires an image to have 10 times as many points as one 12.5 hours newer to be ranked above it
        # While this could be moved to a constant, it is simpler to have it in the query as it's only used once, and using string concating is a bit of a hack when creating queries
        images = db.session.execute(
            "SELECT photo.id, photo.title, photo.path, photo.votes, photo.created_on FROM photo " +
            "ORDER BY ROUND(CAST(LOG(GREATEST(ABS(photo.votes), 1)) * SIGN(photo.votes) + DATE_PART('epoch', photo.created_on) / 45000.0 as NUMERIC), 7) DESC " +
            "OFFSET " + str(app.config["IMAGES_PER_PAGE"] * (page - 1)) + " LIMIT " + str(app.config["IMAGES_PER_PAGE"])
        )

        results = []

        # For now, this returns the image path instead of the image itself
        # This could be properly implemented in 2 ways: Either return all the images now, or just have a route to get an image by id and load them one at a time on the front end
        for row in images:
            results.append({
                "id": row.id,
                "title": row.title,
                "path": row.path,
                "votes": row.votes,
                "creation_date": row.created_on
            })

        return jsonify({
            "status": "Success",
            "data": results
        })

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "status": "Failure",
            "message": "Invalid route"
        })

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            "status": "Failure",
            "message": "Server error. Contact an admin if this problem persists"
        })

    return app
