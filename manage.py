#!./venv/bin/python

import os

from flask_script import Manager
from flask_script.commands import ShowUrls, Clean
from flask_migrate import Migrate, MigrateCommand
from threesixty import create_app
from threesixty.models import db, Photo

# Default to dev config because no one should use this in production anyway
app = create_app('threesixty.settings.DevConfig')
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())
manager.add_command('db', MigrateCommand)


@manager.shell
def make_shell_context():
    """ Creates a python REPL with several default imports
        in the context of the app
    """

    return dict(app=app, db=db, Photo=Photo)


if __name__ == "__main__":
    manager.run()
