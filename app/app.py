#! ../env/bin/python

from flask import Flask, request, jsonify, make_response, send_file
from werkzeug.utils import secure_filename

from .models import db, Photo
from .settings import ProdConfig
from .libs import generateFilename
from io import BytesIO
from PIL import Image
import boto
import os


__author__ = 'Paul Olteanu'
__email__ = 'p.a.olteanu@gmail.com'
__version__ = '1.0'


# Returns a flask app object
# The config can be specified as an argument, or defaults to Prod
def create_app(object_name=ProdConfig):
    """ Returns a flask app object
    The config can be specified as an argument, or defaults to Prod
    """

    # Create the app
    app = Flask(__name__)

    # Set the app config to the speficied one
    app.config.from_object(object_name)

    # Initialize the database helper
    db.init_app(app)

    # A basic route to test if the API is working
    @app.route("/")
    def index():
        return jsonify({
            "status": "Success",
            "message": "Welcome to the API! For specs on the routes, check the readme at https://github.com/PaulOlteanu/Shamrok"
        })

    # Images route. Allows users to get all images, or to upload an image
    @app.route("/images", methods=["GET", "POST"])
    def images():

        # GET route. Returns all images sorted by the specified method, or defaults to oldest -> newest
        # Split into pages of app.config["IMAGES_PER_PAGE"], which is usually 20
        if request.method == "GET":

            # Defaults to page 1
            page = 1

            # Checks if there's a page argument, and makes sure it's valid
            if "page" in request.args.keys():
                try:
                    page = int(request.args["page"])
                except ValueError:
                    response = jsonify({
                        "status": "Failure",
                        "message": "Invalid page number"
                    })

                    # make_response needs to be used to be able to specify the status code
                    return make_response((response, 400))

            # Checks if there's a sort argument, and makes sure it's valid
            if "sort" in request.args.keys() and request.args["sort"] != "new" and request.args["sort"] != "hot":
                response = jsonify({
                    "status": "Failure",
                    "message": "Invalid sort method"
                })

                # make_response needs to be used to be able to specify the status code
                return make_response((response, 400))

            # Thee offset is done by multiplying page - 1 by the number of images on a page
            # Page has 1 subtracted from it because if not, it would be offset by IMAGES_PER_PAGE on the 1st page, and 2 * IMAGES_PER_PAGE on the 2nd one
            # The offset should actually be 0 for the first and IMAGES_PER_PAGE for the 2nd
            if "sort" not in request.args:

                # Default to sorting by creation date
                images = Photo.query.order_by(Photo.created_on).offset(app.config["IMAGES_PER_PAGE"] * (page - 1)).limit(app.config["IMAGES_PER_PAGE"])
            elif request.args["sort"] == "new":

                # Sort by reverse creation date, so new -> old
                images = Photo.query.order_by(Photo.created_on.desc()).offset(app.config["IMAGES_PER_PAGE"] * (page - 1)).limit(app.config["IMAGES_PER_PAGE"])
            else:

                # Implementation of reddit's hot sorting algorithm in SQL
                # This is implemented in SQL because it's sorting in the database and limiting to the number of images per page is more efficient than getting the whole table
                # The number of images per page is set in the config

                # 45000 is a magic number in reddit's code too. It's the number of seconds in 12.5 hours
                # The way the algorithm works requires an image to have 10 times as many points as one 12.5 hours newer to be ranked above it
                # While this could be moved to a constant, it is simpler to have it in the query as it's only used once,
                # and using string concating is a bit of a hack when creating queries
                images = db.session.execute(
                    "SELECT photo.id, photo.title, photo.filename, photo.mimetype, photo.votes, photo.created_on FROM photo " +
                    "ORDER BY ROUND(CAST(LOG(GREATEST(ABS(photo.votes), 1)) * SIGN(photo.votes) + DATE_PART('epoch', photo.created_on) / 45000.0 as NUMERIC), 7) DESC " +
                    "OFFSET " + str(app.config["IMAGES_PER_PAGE"] * (page - 1)) + " LIMIT " + str(app.config["IMAGES_PER_PAGE"])
                )

            results = []

            # Loop through images and create the response
            for image in images:
                results.append({
                    "id": image.id,
                    "title": image.title,
                    "filename": image.filename,
                    "mimetype": image.mimetype,
                    "votes": image.votes,
                    "creation_date": image.created_on
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
                response = jsonify({
                    "status": "Failure",
                    "message": "File missing"
                })

                # make_response needs to be used to be able to specify the status code
                return make_response((response, 400))

            upload = request.files["file"]

            # Make sure the file extension is valid
            if upload.filename.split(".")[-1] not in ["png", "jpg", "bmp", "jpeg"]:
                response = jsonify({
                    "status": "Failure",
                    "message": "Invalid file extension"
                })

                # make_response needs to be used to be able to specify the status code
                return make_response((response, 400))

            # Make sure a title is present
            if "title" not in request.form.keys():
                response = jsonify({
                    "status": "Failure",
                    "message": "Title missing"
                })

                # make_response needs to be used to be able to specify the status code
                return make_response((response, 400))
            else:
                title = request.form["title"]

            # Open image for compressing
            image = Image.open(upload)

            # File to save the image to. The filename is randomly generated from the generateFilname function
            # TODO: Check for a collision with an already existing filename
            new_filename = secure_filename(generateFilename(app.config["IMAGE_NAME_LENGTH"]) + "." + upload.filename.split(".")[-1])

            # Prod connects to Amazon S3
            if app.config["ENV"] == "prod":

                # Get the list of buckets and then a specific bucket
                conn = boto.connect_s3(app.config["S3_KEY"], app.config["S3_SECRET"])
                b = conn.get_bucket(app.config["S3_BUCKET"])

                # Create a temporary "file" to save the image to
                # This allows compression to be applied as compression only happens when the image is saved
                s3_file = BytesIO()

                # Save the image and compress it thanks to the quality and optimize arguments
                # The format is normally set to the exptension of the uploaded file, but the correct format for .jpg is jpeg
                # This is checked for and set to jpeg if the file extension is .jpg
                image.save(s3_file, quality=40, optimize=True, format="jpeg" if upload.filename.split(".")[-1].lower() != "jpg" else upload.filename.split(".")[-1])

                # Set the file name of the s3 file as it's not set from image.save
                s3_file.name = new_filename

                # Return the file pointer to the start of the file
                # This is required before setting the contents of the final file to upload
                s3_file.seek(0)

                # An s3 "key" is basically a file name
                # The contents are set to the file from above
                # The file is then made publically readable so that all users can view it
                sml = b.new_key("/".join([app.config["S3_UPLOAD_DIRECTORY"], new_filename]))
                sml.set_contents_from_file(s3_file, headers={'Content-Type': upload.mimetype})
                sml.set_acl('public-read')

            else:
                # Save the image and compress it thanks to the quality and optimize arguments
                image.save(os.path.join(app.config["IMAGE_FOLDER"], new_filename), quality=40, optimize=True)

            image.close()

            # Create a database entry for the new image
            photo = Photo(title=title, filename=secure_filename(new_filename), mimetype=upload.mimetype)
            db.session.add(photo)
            db.session.commit()

            return jsonify({
                "status": "Success"
            })

    @app.route("/images/<int:image_id>")
    def get_image(image_id):
        photo = Photo.query.filter_by(id=image_id).first()

        # Make sure the image with the specified id exists
        if not photo:
            response = jsonify({
                "status": "Failure",
                "message": "Photo id does not exist"
            })

            # make_response needs to be used to be able to specify the status code
            return make_response((response, 400))

        # Prod connects to Amazon S3
        if app.config["ENV"] == "prod":

            # Get the list of buckets and then a specific bucket
            conn = boto.connect_s3(app.config["S3_KEY"], app.config["S3_SECRET"])
            b = conn.get_bucket(app.config["S3_BUCKET"])

            # Get the image with the matching filename
            item = b.get_key("/".join([app.config["S3_UPLOAD_DIRECTORY"], photo.filename]))

            # Open the image to read
            item.open_read()

            # Send the file, along with the stored mimetype
            return send_file(item, mimetype=photo.mimetype)

            item.close()

        else:

            # Send the file by matching the database filename to the one on disk
            # Avoids having to load it
            return send_file(os.path.join(app.config["IMAGE_FOLDER"], photo.filename), mimetype=photo.mimetype)

    # Route to upvote an image
    @app.route("/images/upvote/<int:image_id>", methods=["POST"])
    def upvote(image_id):
        photo = Photo.query.filter_by(id=image_id).first()

        # Make sure the image with the specefied id exists
        if not photo:
            response = jsonify({
                "status": "Failure",
                "message": "Photo id does not exist"
            })

            # make_response needs to be used to be able to specify the status code
            return make_response((response, 400))

        # Upvote the image and save it to the database
        photo.votes += 1
        db.session.commit()

        return jsonify({
            "status": "Success",
            "message": "Upvoted image"
        })

    # Error handling routes
    # One for invalid routes, and one for server errors
    @app.errorhandler(404)
    def not_found_error(error):
        response = jsonify({
            "status": "Failure",
            "message": "Invalid route"
        })

        # make_response needs to be used to be able to specify the status code
        return make_response((response, 404))

    @app.errorhandler(500)
    def internal_error(error):

        # Roll back the database to a valid state
        db.session.rollback()

        response = jsonify({
            "status": "Failure",
            "message": "Server error. Contact an admin if this problem persists"
        })

        # make_response needs to be used to be able to specify the status code
        return make_response((response, 500))

    return app
