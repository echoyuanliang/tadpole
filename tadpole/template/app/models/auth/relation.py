#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/19 by allen
"""

from datetime import datetime
from app.lib.database import db, Column

user_role = db.Table('user_role',
                     Column('user_id', db.Integer, db.ForeignKey('user.id')),
                     Column('role_id', db.Integer, db.ForeignKey('role.id')),
                     Column('create_date', db.DateTime, nullable=False, default=datetime.now))


role_resource = db.Table('role_resource',
                         Column('role_id', db.Integer, db.ForeignKey('role.id')),
                         Column('resource_id', db.Integer, db.ForeignKey('resource.id')),
                         Column('create_date', db.DateTime, nullable=False, default=datetime.now))
