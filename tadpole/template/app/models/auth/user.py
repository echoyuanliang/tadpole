#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/7 by allen
"""

from app.lib.database import db, Column
from app.lib.database import MysqlModel as Model


class User(Model):

    # columns in __hide__ does'nt show in rest_db
    __hide__ = ('password',)

    account = Column(
        db.String(128),
        nullable=False,
        default=u'-',
        index=True,
        unique=True)
    name = Column(db.String(32), nullable=False, default=u'-')
    email = Column(db.Email(128), nullable=False, default=u'-')
    password = Column(db.Password(schemes=['pbkdf2_sha512', 'md5_crypt'],
                                  deprecated=['md5_crypt']), nullable=False, default=u'-')

    def validate_password(self, password):
        return self.password == password
