import pytest
import os

from app import create_app
from app.models import db, Photo


@pytest.fixture()
def testapp(request):
    app = create_app('app.settings.TestConfig')
    client = app.test_client()

    db.app = app
    db.create_all()

    if getattr(request.module, "create_photo", True):
        photo = Photo('Title', '/path')
        db.session.add(photo)
        db.session.commit()

    def teardown():
        db.session.remove()
        db.drop_all()

        for f in os.listdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), "images")):
            os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), "images", f))


    request.addfinalizer(teardown)

    return client
