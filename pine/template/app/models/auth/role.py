# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/7 by allen
"""

from app.lib.database import db, Column
from app.lib.database import MysqlModel as Model
from relation import user_role, role_resource


class Role(Model):

    name = Column(db.String(32), nullable=False, default='-', index=True, unique=True)
    description = Column(db.String(128), nullable=False, default='-')

    users = db.relationship('User', secondary=user_role,
                            backref=db.backref('roles', lazy='dynamic'),
                            lazy='dynamic')

    resources = db.relationship('Resource', secondary=role_resource,
                                backref=db.backref('roles', lazy='dynamic'),
                                lazy='dynamic')
