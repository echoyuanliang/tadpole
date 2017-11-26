#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/6 by allen
"""

from ipaddress import ip_address
from sqlalchemy import types
from app.lib.database.utils import ConversionBase


class IpAddressType(types.TypeDecorator, ConversionBase):
    impl = types.BigInteger

    def __init__(self, *args, **kwargs):

        super(IpAddressType, self).__init__(*args, **kwargs)
        self.impl = types.BigInteger

    def process_bind_param(self, value, dialect):
        if isinstance(value, basestring):
            return int(ip_address(value))
        else:
            return int(value)

    def process_result_value(self, value, dialect):
        return ip_address(value) if value else None

    def _conversion(self, value):
        return ip_address(value) if value else None

    @property
    def python_type(self):
        return self.impl.type.python_type
