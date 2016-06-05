#! ../env/bin/python
# -*- coding: utf-8 -*-

import pytest

from threesixty.models import db, Photo

create_user = False


@pytest.mark.usefixtures("testapp")
class TestModels:

    def test_photo_save(self, testapp):
        """ Test saving the photo model to the database """

        photo = Photo('Title', '/path')
        db.session.add(photo)
        db.session.commit()

        photo = Photo.query.filter_by(title="Title").first()
        assert photo is not None

    def test_photo_path_setting(self, testapp):
        """ Test photo path saving """

        photo = Photo('Title', '/path')

        assert photo.title == 'Title'
        assert photo.path == '/path'
