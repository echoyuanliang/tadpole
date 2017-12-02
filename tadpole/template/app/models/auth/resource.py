#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/19 by allen
"""

from sqlalchemy import Index
from app.lib.database import db, Column
from app.lib.database import MysqlModel as Model


class Resource(Model):
    rtype = Column(db.String(32), nullable=False, default=u'-')
    name = Column(db.String(128), nullable=False, default=u'-')
    operation = Column(db.String(32), nullable=False, default=u'-')
    description = Column(db.String(128), nullable=False, default=u'-')


Index('name_operation_uc', Resource.name, Resource.operation, unique=True)
