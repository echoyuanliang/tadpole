#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/6 by allen
"""

from abc import abstractmethod
import sqlalchemy as sa


class ConversionBase(object):

    @abstractmethod
    def _conversion(self, value):
        raise NotImplementedError

    def conversion_listener(self, target, value, oldvalue, initiator):
        return self._conversion(value)


def conversion_listener(mapper, class_):

    for prop in mapper.iterate_properties:
        try:
            listener = prop.columns[0].type.conversion_listener
        except AttributeError:
            continue
        sa.event.listen(
            getattr(class_, prop.key),
            'set',
            listener,
            retval=True
        )


def auto_conversion(mapper=None):
    if mapper is None:
        mapper = sa.orm.mapper
    sa.event.listen(mapper, 'mapper_configured', conversion_listener)


def inspect_type(mixed):
    if isinstance(mixed, sa.orm.attributes.InstrumentedAttribute):
        return mixed.property.columns[0].type
    elif isinstance(mixed, sa.orm.ColumnProperty):
        return mixed.columns[0].type
    elif isinstance(mixed, sa.Column):
        return mixed.type


def is_case_insensitive(mixed):
    try:
        return isinstance(
            inspect_type(mixed).comparator,
            CaseInsensitiveComparator
        )
    except AttributeError:
        try:
            return issubclass(
                inspect_type(mixed).comparator_factory,
                CaseInsensitiveComparator
            )
        except AttributeError:
            return False


class CaseInsensitiveComparator(sa.Unicode.Comparator):

    def __init__(self, *args, **kwargs):
        super(CaseInsensitiveComparator, self).__init__(*args, **kwargs)

    @classmethod
    def lowercase_arg(cls, func):
        def operation(self, other, **kwargs):
            operator = getattr(sa.Unicode.Comparator, func)
            if other is None:
                return operator(self, other, **kwargs)
            if not is_case_insensitive(other):
                other = sa.func.lower(other)
            return operator(self, other, **kwargs)
        return operation

    def in_(self, other):
        if isinstance(other, list) or isinstance(other, tuple):
            other = map(sa.func.lower, other)
        return sa.Unicode.Comparator.in_(self, other)

    def notin_(self, other):
        if isinstance(other, list) or isinstance(other, tuple):
            other = map(sa.func.lower, other)
        return sa.Unicode.Comparator.notin_(self, other)
