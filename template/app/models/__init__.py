# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/7 by allen
"""

from auth import *


def create_db():
    from app.lib.database import db
    db.create_all()
    User.query.all()
