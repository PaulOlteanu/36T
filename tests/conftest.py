import pytest

from threesixty import create_app
from threesixty.models import db, Photo


@pytest.fixture()
def testapp(request):
    app = create_app('threesixty.settings.TestConfig')
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

    request.addfinalizer(teardown)

    return client
