#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/6 by allen
"""

import weakref
from passlib.context import LazyCryptContext
from sqlalchemy import types
from sqlalchemy.ext.mutable import Mutable
from app.lib.database.utils import ConversionBase


class Password(Mutable, object):

    @staticmethod
    def coerce(cls, key, value):
        if isinstance(value, Password):
            return value

        if isinstance(value, basestring):
            return cls(value, secret=True)

        super(Password, cls).coerce(key, value)

    def __init__(self, value, context, secret=False):
        self.hash = value if not secret else None
        self.secret = value if secret else None

        if isinstance(self.hash, unicode):
            self.hash = self.hash.encode("utf-8")

        self.context = weakref.proxy(context) if context is not None else None

    def __eq__(self, value):
        if self.hash is None or value is None:
            return self.hash is None

        if isinstance(value, Password):
            return self.hash == value.hash

        if self.context is None:
            return value == self

        if isinstance(value, basestring):
            valid, new = self.context.verify_and_update(value, self.hash)

            if valid and new:
                self.hash = new

            if isinstance(self.hash, unicode):
                self.hash = self.hash.encode('utf-8')
                self.changed()

            return valid

        return False

    def _as_dict(self):
        return self.hash


class PasswordType(types.TypeDecorator, ConversionBase):

    python_type = Password
    impl = types.VARBINARY(1024)

    def __init__(self, max_length=None, **kwargs):
        self._max_length = max_length
        self.context = LazyCryptContext(**kwargs)

        super(PasswordType, self).__init__()

    @property
    def length(self):
        if self._max_length is None:
            self._max_length = self.calculate_max_length()

        return self._max_length

    def calculate_max_length(self):

        max_lengths = [1024]
        for name in self.context.schemes():
            scheme = getattr(__import__('passlib.hash').hash, name)
            length = 4 + len(scheme.name)
            length += len(str(getattr(scheme, 'max_rounds', '')))
            length += (getattr(scheme, 'max_salt_size', 0) or 0)
            length += getattr(
                scheme,
                'encoded_checksum_size',
                scheme.checksum_size
            )
            max_lengths.append(length)

        return max(max_lengths)

    def load_dialect_impl(self, dialect):
        impl = types.VARBINARY(self.length)
        return dialect.type_descriptor(impl)

    def process_bind_param(self, value, dialect):
        if isinstance(value, Password):
            if value.secret is not None:
                return value.context.encrypt(value.secret).encode("utf-8")

            return value.hash

        if isinstance(value, basestring):
            return self.context.encrypt(value).encode("utf-8")

    def process_result_value(self, value, dialect):
        if value is not None:
            return Password(value, self.context)

    def _conversion(self, value):
        if value is None:
            return

        if not isinstance(value, Password):
            value = self.context.encrypt(value).encode("utf-8")
            return Password(value, context=self.context, secret=False)

        else:
            value.context = weakref.proxy(self.context)
            if value.secret:
                value.hash = value.context.encrypt(value.secret).encode("utf-8")
                value.secret = None

            return value
