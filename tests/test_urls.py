#! ../venv/bin/python

import pytest
import os
from flask import json
from app.models import db, Photo

create_photo = True


@pytest.mark.usefixtures("testapp")
class TestURLs:

    def test_404(self, testapp):
        """ Tests if invalid routs return 404s """

        rv = testapp.get("404")

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 404
        assert return_data["status"] == "Failure"

    def test_home(self, testapp):
        """ Tests if the index route loads """

        rv = testapp.get("/")
        assert rv.status_code == 200

    def test_get_images_status(self, testapp):
        """ Tests if image GET route loads """

        rv = testapp.get("/images")

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 200
        assert return_data["status"] == "Success"

    def test_get_images_data(self, testapp):
        """ Tests if image GET route returns images """

        rv = testapp.get("/images")

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 200
        assert return_data["status"] == "Success"

        assert return_data["data"]

    def test_image_upload(self, testapp):
        """ Tests whether image uploading works """

        basedir = os.path.abspath(os.path.dirname(__file__))

        with open(os.path.join(basedir, "test.jpg"), "rb") as image:
            rv = testapp.post("/images", data=dict(title="HLH", file=image))

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 200
        assert return_data["status"] == "Success"

        photo = photo = Photo.query.filter_by(title="HLH").first()

        assert photo

    def test_missing_file_error(self, testapp):
        """ Tests if not including a file errors out """

        rv = testapp.post("/images", data=dict(title="HLH",))

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 400
        assert return_data["status"] == "Failure"

    def test_missing_title_error(self, testapp):
        """ Tests if not including a title errors out """

        basedir = os.path.abspath(os.path.dirname(__file__))

        with open(os.path.join(basedir, "test.jpg"), "rb") as image:
            rv = testapp.post("/images", data=dict(file=image))

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 400
        assert return_data["status"] == "Failure"

    def test_invalid_extension(self, testapp):
        """ Tests if uploading an invalid extension errors out """

        basedir = os.path.abspath(os.path.dirname(__file__))

        with open(os.path.join(basedir, "test.jkl")) as f:
            rv = testapp.post("/images", data=dict(file=f))

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 400
        assert return_data["status"] == "Failure"

    def test_new_page_one(self, testapp):
        """ Test if the last item in /images?sort=new has the id of 1 """

        rv = testapp.get("/images?sort=new&page=1")

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 200
        assert return_data["status"] == "Success"
        assert return_data["data"][0]["id"] == 1

    def test_new_other_pages(self, testapp):
        """ Test if the last item in /images?sort=new&page=2 has the id of 1 """

        basedir = os.path.abspath(os.path.dirname(__file__))

        # HACK: Adding i to the path is bad, but there's no way around the unique constraint on the path column
        # Really, the path doesn't matter for this test though so it's not that bad
        for i in range(20):
            db.session.add(Photo(title="Title", filename=os.path.join(basedir, str(i) + "test.jpg"), mimetype="image/jpg"))

        db.session.commit()

        rv = testapp.get("/images?sort=new&page=2")

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 200
        assert return_data["status"] == "Success"

        # The id should still be 1 because pages are 20 images, and it has 20 images before it
        # This means it'll be the first one on the 2nd page
        assert return_data["data"][0]["id"] == 1

    def test_invalid_page_number_new(self, testapp):
        """ Test if an invalid page value errors out """

        rv = testapp.get("/images?sort=new&page=jkl")

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 400
        assert return_data["status"] == "Failure"

    def test_hot_sort(self, testapp):
        """ Test the hot sorting algorithm """

        basedir = os.path.abspath(os.path.dirname(__file__))

        photo = Photo(title="Title", filename=os.path.join(basedir, "test.jpg"), mimetype="image/jpg", votes=1)
        db.session.add(photo)
        db.session.commit()

        rv = testapp.get("/images?sort=hot&page=1")

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 200
        assert return_data["status"] == "Success"

        # Should be 2 because it has more upvotes than the default one
        assert return_data["data"][0]["id"] == 2

    def test_invalid_page_number_hot(self, testapp):
        """ Test if an invalid page value errors out """

        rv = testapp.get("/images?sort=hot&page=jkl")

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 400
        assert return_data["status"] == "Failure"

    def test_invalid_sort(self, testapp):
        """ Test if an invalid sort option errors out """

        rv = testapp.get("/images?sort=sdaf")

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 400
        assert return_data["status"] == "Failure"

    def test_upvote(self, testapp):
        """ Test if upvoting works """

        votesPrev = Photo.query.filter_by(id=1).first().votes

        testapp.post("/images/upvote/1")

        votesNew = Photo.query.filter_by(id=1).first().votes

        assert votesNew == votesPrev + 1

    def test_nonexistant_id_upvote(self, testapp):
        """ Test if upvoting a nonexistant id errors out """

        rv = testapp.post("/images/upvote/2")

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 400
        assert return_data["status"] == "Failure"

    def test_get_image(self, testapp):
        """ Test getting a specific image """

        basedir = os.path.abspath(os.path.dirname(__file__))

        rv=testapp.get("/images/1")

        with open(os.path.join(basedir, "images/test.jpg"), "rb") as image:
            assert rv.get_data() == image.read()

    def test_get_image_invalid_id(self, testapp):
        """ Test if getting an id that doesn't exist errors out """

        rv = testapp.get("/images/2")

        return_data = json.loads(rv.get_data())

        assert rv.status_code == 400
        assert return_data["status"] == "Failure"
