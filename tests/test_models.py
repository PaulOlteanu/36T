#! ../venv/bin/python

import pytest

from app.models import db, Photo
from sqlalchemy.exc import IntegrityError

create_photo = False


@pytest.mark.usefixtures("testapp")
class TestModels:

    def test_photo_save(self, testapp):
        """ Test saving the photo model to the database """

        photo = Photo(title='Title', filename='test.jpg', mimetype="images/jpg")
        db.session.add(photo)
        db.session.commit()

        photo = Photo.query.filter_by(title="Title").first()
        assert photo is not None

    def test_photo_repr(self, testapp):
        """ Test the repr function returning the full representation """

        photo = Photo(title="Title", filename="test.jpg", mimetype="image/jpg")

        assert repr(photo) == "<Photo ID: {}, Title: {}, Votes: {}, Creation_Date: {}>".format(photo.id, photo.title, photo.votes, photo.created_on)

        db.session.add(photo)
        photo = Photo.query.first()

        assert repr(photo) == "<Photo ID: {}, Title: {}, Votes: {}, Creation_Date: {}>".format(photo.id, photo.title, photo.votes, photo.created_on)

    def test_duplicate_path_error(self, testapp):
        """ Test whether saving 2 models with the same path errors out """

        photo1 = Photo(title="Title", filename="test.jpg", mimetype="image/jpg")
        photo2 = Photo(title="Title", filename="test.jpg", mimetype="image/jpg")

        db.session.add(photo1)
        db.session.commit()

        with pytest.raises(IntegrityError):
            db.session.add(photo2)
            db.session.commit()
