#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/7 by allen
"""

from app.lib.database import db, Column
from app.lib.database import MysqlModel as Model


class User(Model):

    __hide__ = ('password',)

    account = Column(db.String(128), nullable=False, default='-', index=True, unique=True)
    name = Column(db.String(32), nullable=False, default='-')
    email = Column(db.Email(128), nullable=False, default='-')
    password = Column(db.Password(schemes=['pbkdf2_sha512', 'md5_crypt'],
                                  deprecated=['md5_crypt']), nullable=False, default='-')

    def validate_password(self, password):
        return self.password == password
