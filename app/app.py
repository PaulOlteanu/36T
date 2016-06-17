#! ../env/bin/python

from flask import Flask, request, jsonify, make_response, send_file, render_template, url_for
from werkzeug.utils import secure_filename

from .models import db, Photo
from .settings import ProdConfig
from .lib import generate_filename, get_images_sort_old, get_images_sort_new, get_images_sort_hot
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

    app.url_map.strict_slashes = False

    # Initialize the database helper
    db.init_app(app)

    # TEMPLATE ROUTES ==============================================================================================================================================================

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/images")
    def images():

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

        # The offset needs to be page - 1 because if not, it would be offset by IMAGES_PER_PAGE on the 1st page, and 2 * IMAGES_PER_PAGE on the 2nd one
        # The offset should actually be 0 for the 1st page and IMAGES_PER_PAGE for the 2nd
        page -= 1

        if page < 0:
            page = 0

        # Checks if there's a sort argument, and makes sure it's valid
        if "sort" in request.args.keys() and request.args["sort"].lower() != "old" and request.args["sort"].lower() != "new" and request.args["sort"].lower() != "hot":
            response = jsonify({
                "status": "Failure",
                "message": "Invalid sort method"
            })

            # make_response needs to be used to be able to specify the status code
            return make_response((response, 400))

        if "sort" not in request.args or request.args["sort"].lower() == "old":

            # Default to sorting by creation date
            images = get_images_sort_old(page, app.config["IMAGES_PER_PAGE"])
            sort = "old"
        elif request.args["sort"].lower() == "new":

            # Sort by reverse creation date, so new -> old
            images = get_images_sort_new(page, app.config["IMAGES_PER_PAGE"])
            sort = "new"
        else:

            # Sort by the hot sort algorithm
            images = get_images_sort_hot(page, app.config["IMAGES_PER_PAGE"])
            sort = "hot"

        results = []

        # Loop through images and create the data to render the template with
        for image in images:
            results.append({
                "id": image.id,
                "title": image.title,
                "image_url": url_for("api_return_image", image_id=image.id, _external=True),
                "votes": image.votes,
            })

        # Page is increased by one because it becomes decremented by one after the submission
        return render_template("images.html", images=results, sort=sort, header=sort.capitalize(), page=page + 1)

    @app.route("/upload")
    def upload():
        return render_template("upload.html")

    # API ROUTES ===================================================================================================================================================================

    # A basic route to test if the API is working
    @app.route("/api")
    def api_index():
        return jsonify({
            "status": "Success",
            "message": "Welcome to the API! For specs on the routes, check the readme at https://github.com/PaulOlteanu/Shamrok"
        })

    # Images route. Allows users to get all images, or to upload an image
    @app.route("/api/images", methods=["GET", "POST"])
    def api_images():

        # GET route. Returns all images sorted by the specified method, or defaults to oldest -> newest
        # Split into pages of app.config["IMAGES_PER_PAGE"], which is usually 10
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

            # The offset needs to be page - 1 because if not, it would be offset by IMAGES_PER_PAGE on the 1st page, and 2 * IMAGES_PER_PAGE on the 2nd one
            # The offset should actually be 0 for the 1st page and IMAGES_PER_PAGE for the 2nd
            page -= 1

            if page < 0:
                page = 0

            # Checks if there's a sort argument, and makes sure it's valid
            if "sort" in request.args.keys() and request.args["sort"].lower() != "new" and request.args["sort"].lower() != "hot":
                response = jsonify({
                    "status": "Failure",
                    "message": "Invalid sort method"
                })

                # make_response needs to be used to be able to specify the status code
                return make_response((response, 400))

            if "sort" not in request.args:

                # Default to sorting by creation date
                images = get_images_sort_old(page, app.config["IMAGES_PER_PAGE"])
            elif request.args["sort"].lower() == "new":

                # Sort by reverse creation date, so new -> old
                images = get_images_sort_new(page, app.config["IMAGES_PER_PAGE"])
            else:

                # Sort by the hot sort algorithm
                images = get_images_sort_hot(page, app.config["IMAGES_PER_PAGE"])

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

            # File to save the image to. The filename is randomly generated from the generate_filname function
            # TODO: Check for a collision with an already existing filename
            new_filename = secure_filename(generate_filename(app.config["IMAGE_NAME_LENGTH"]) + "." + upload.filename.split(".")[-1])

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

    @app.route("/api/images/<int:image_id>")
    def api_return_image(image_id):
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
    @app.route("/api/images/upvote/<int:image_id>", methods=["POST"])
    def api_upvote(image_id):
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
