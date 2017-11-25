# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/6 by allen
"""

import re
import sqlalchemy as sa
from sqlalchemy import types
from app.lib.database.utils import CaseInsensitiveComparator


class EmailType(types.TypeDecorator):

    impl = sa.Unicode
    comparator_factory = CaseInsensitiveComparator
    re_exp = re.compile(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$")

    def __init__(self, length=255, *args, **kwargs):
        super(EmailType, self).__init__(length=length, *args, **kwargs)

    def _validate(self, value):
        if not self.re_exp.match(value):
            raise ValueError('invalid email format %s' % value)
        return value

    def process_bind_param(self, value, dialect):
        if value is not None:
            return self._validate(value.lower())
        return value

    @property
    def python_type(self):
        return self.impl.type.python_type
