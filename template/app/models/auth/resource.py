# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/19 by allen
"""


from app.lib.database import db, Column
from app.lib.database import MysqlModel as Model


class Resource(Model):
    rtype = Column(db.String(32), nullable=False, default='-')
    name = Column(db.String(128), nullable=False, default='-')
    operation = Column(db.String(32), nullable=False, default='-')
    description = Column(db.String(128), nullable=False, default='-')
