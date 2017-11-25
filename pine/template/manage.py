# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/4 by allen
"""

from flask_script import Manager, Server, Shell
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
manager.add_command('server', Server(host=app.config.get('HOST', '0.0.0.0'),
                                     port=app.config.get('PORT', 8080)))
manager.add_command('dev', Server(host=app.config.get('HOST', '127.0.0.1'),
                                  port=app.config.get('PORT', 5000), use_debugger=True))
manager.add_command("shell", Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()
