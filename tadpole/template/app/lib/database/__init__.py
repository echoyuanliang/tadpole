#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/7 by allen
"""

from datetime import datetime

from app.extensions.sqlalchemy import extension as db
from app.lib.utils import get_relation_url
from sqlalchemy import inspect

import custom_types

Column = db.Column


class CRUDMixin(object):

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    @classmethod
    def query_update(cls, query=None, data=None):
        query = query or dict()
        update_query = getattr(cls, 'query').filter_by(**query)
        update_query.update(data or dict())
        db.session.commit()
        return update_query.all()

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()


class SurrogatePK(object):

    __table_args__ = {'extend_existing': True}

    @classmethod
    def get(cls, record_id):
        data = getattr(cls, 'query').get(record_id)
        return data

    @classmethod
    def get_by(cls, **kwargs):
        return getattr(cls, 'query').filter_by(**kwargs)


class Model(SurrogatePK, db.Model, CRUDMixin):
    __abstract__ = True

    id = Column(db.Integer, nullable=False, primary_key=True)
    create_time = Column(db.DateTime, nullable=False,
                         default=datetime.now, onupdate=datetime.now)

    @classmethod
    def get_columns(cls):
        return cls.__table__.columns

    @classmethod
    def get_column_names(cls):
        return [c.name for c in cls.get_columns()]

    def _as_dict(self):  # for common sqlalchemy  query result to dict
        from main import app
        hide_attrs = getattr(self, '__hide__', ())

        column_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns
                       if c.name not in hide_attrs}

        try:
            for rel_name, _ in inspect(type(self)).relationships.items():
                if rel_name in hide_attrs:
                    continue

                column_dict['__' + rel_name + '_link'] = get_relation_url(
                    self.__tablename__, self.id, rel_name)

        except Exception as e:
            app.logger.info(str(e))

        return column_dict

    def to_dict(self):  # for human
        return self._as_dict()


class MysqlModel(Model):

    __abstract__ = True
    __table_args_ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }


def reference_col(tablename, nullable=False, pk_name='id', **kwargs):

    return db.Column(
        db.ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)


def get_model_registry():
    return (model for model in getattr(db.Model, '_decl_class_registry').values()
            if hasattr(model, '__tablename__'))


def get_model_by_tablename(tablename):
    model_registry = get_model_registry()

    for c in model_registry:
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c


def query_result2dict(result_item):
    if callable(getattr(result_item, '_as_dict', None)):
        return getattr(result_item, '_as_dict')()
    elif callable(getattr(result_item, 'to_dict', None)):
        return getattr(result_item, 'to_dict')()
    elif getattr(result_item, '_fields', []):
        return {field: getattr(result_item, field, None)
                for field in getattr(result_item, '_fields')}

    raise ValueError(u'convert query result item {0}, {1} to dict failed'.
                     format(type(result_item), result_item))


def include_custom_types(obj):
    for key in custom_types.__all__:
        if not hasattr(obj, key):
            setattr(obj, key, getattr(custom_types, key))

include_custom_types(db)

