#!venv/bin/python
# coding: utf-8

"""
    create at 2017/11/4 by allen
"""

from flask_script import Manager, Shell
from flask_script.commands import ShowUrls, Clean

from app import models
from app.lib.database import db
from main import app

manager = Manager(app)


def _make_context():
    return dict(app=app, db=db)


@manager.command
def create_db():
    models.create_db()

manager.add_command('url', ShowUrls())
manager.add_command('clean', Clean())
manager.add_command("shell", Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()
