#! ../venv/bin/python

import pytest

from app.lib import generate_filename

create_photo = False


@pytest.mark.usefixtures("testapp")
class TestLibs:

    def test_random_name_length(self, testapp):
        """ Test random name generator is correct length """

        assert len(generate_filename(5)) == 5
