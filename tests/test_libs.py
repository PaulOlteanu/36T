#! ../venv/bin/python

import pytest

from app.libs import generateFilename

create_photo = False


@pytest.mark.usefixtures("testapp")
class TestLibs:

    def test_random_name_length(self, testapp):
        """ Test random name generator is correct length """

        assert len(generateFilename(5)) == 5
