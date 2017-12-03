#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/12 by allen
"""


import urllib
from copy import copy
from collections import namedtuple
from flask import request
from sqlalchemy.inspection import inspect
from app.lib.utils import rest_abort
from app.lib.exceptions import ValidationError
from app.lib.database import db, get_model_by_tablename, query_result2dict


_Filter = namedtuple('_Filter', ['key', 'op', 'val'])
_Order = namedtuple('_Order', ['key', 'order'])


class ModelWrapper(object):
    OPERATORS = ('lt', 'le', 'gt', 'ge', 'eq', 'like', 'in', 'between')

    # use __ prefix distinct with model columns

    PROCESSES = ('__show', '__order')
    PAGINATE = ('__page', '__page_size')

    def __init__(self, app, name, model):
        self.app = app
        self.name = name
        self.model = model
        self.columns = self.model.get_column_names()
        self.default_page_size = self.app.config.get('DEFAULT_PAGE_SIZE', 200)
        self.min_page_size = self.app.config.get('MIN_PAGE_SIZE', 10)
        self.max_page_size = self.app.config.get('MAX_PAGE_SIZE', 1000)
        self.value_separator = self.app.config.get('ITEM_SEPARATOR', ',')
        self.operator_separator = self.app.config.get(
            'OPERATOR_SEPARATOR', '.')
        self.default_order = self.app.config.get('DEFAULT_ORDER', 'desc')
        self.suffix_like = self.app.config.get('SUFFIX_LIKE', True)

    def parse_paginate(self, key, value):

        assert key in self.PAGINATE

        page_error = u'param __page must be a positive integer,' \
                     u'your value is {0}'.format(value)

        page_size_error = u'param __page_size must be a positive ' \
                          u'integer between ({0}, {1}), your value is {2}'.\
            format(self.min_page_size, self.max_page_size, value)

        if key == '__page':
            try:
                page = int(value)
            except ValueError:
                raise ValidationError(page_error)

            if page < 1:
                raise ValidationError(page_error)

            return page
        elif key == '__page_size':
            try:
                page_size = int(value)
            except ValueError:
                raise ValidationError(page_size_error)

            return max(min(page_size, self.max_page_size), self.min_page_size)

    def parse_process(self, key, value):
        assert key in self.PROCESSES
        values = [item.strip() for item in value.split(self.value_separator)]
        if not values:
            raise ValidationError(u'{0} must not empty, your value is {1}'.
                                  format(key, value))

        if key == '__show':
            invalid_item = set(values) - set(self.columns)
            if invalid_item:
                raise ValidationError(u'{0} of your __show columns {1} is not'
                                      u' an attribute of {2}  '.format(
                                       u','.join(invalid_item), value, self.name))

            return values
        elif key == '__order':
            order_by_columns = []
            for val in values:
                if val.endswith(('.desc', '.asc')):
                    attr, order = val.split('.')
                else:
                    attr, order = val, self.default_order

                if attr not in self.columns:
                    raise ValidationError(u'{0}  of your __order_by columns '
                                          u'is not an attribute of {1}'.format(
                                           attr, value, self.name))

                order_by_columns.append(_Order(key=attr, order=order))

            return order_by_columns

    def parse_filter(self, key, value):
        if key in self.columns:
            return _Filter(key=key, op='eq', val=value)
        elif key.endswith(self.OPERATORS):
            key_oper = key.split(self.operator_separator)
            if len(key_oper) != 2:
                raise ValidationError(u'invalid filter  {0} for {1}'.format(
                    key, self.name))

            fkey, oper = key_oper

            if fkey not in self.columns:
                raise ValidationError(u'filter key {0} is not an attribute of {1}'.format(
                    fkey, self.name
                ))
            elif oper not in self.OPERATORS:
                raise ValidationError(u'filter operation {0} is not support'.format(oper))

            if oper == 'like' and not self.suffix_like and value.startswith('%'):
                raise ValidationError(u'suffix like is not support, you used at {0}={1}'.format(
                    key, value))
            elif oper in ['in', 'between']:
                value = value.split(self.value_separator)
                if oper == 'between' and len(value) != 2:
                    raise ValidationError(u'between value must be a range,'
                                          u' your query: {0}={1}'.format(
                                           key, self.value_separator.join(value)))

            return _Filter(key=fkey, op=oper, val=value)

        raise ValidationError(u'invalid filter {0} for {1}'.format(
            key, self.name))

    def get_show_query(self, show_columns):
        if show_columns:
            show_columns = [getattr(self.model, column) for column in show_columns]
            return db.session.query(*show_columns)
        else:
            return db.session.query(self.model)

    def order_query(self, query, orders):
        for order in orders:
            if order.order == 'desc':
                query = query.order_by(getattr(self.model, order.key))
            else:
                query = query.order_by(-getattr(self.model, order.key))

        return query

    @staticmethod
    def paginate_query(query, page, page_size):
        offset = (page - 1) * page_size
        return query.offset(offset).limit(page_size)

    def filter_query(self, query, filters):

        for query_filter in filters:
            filter_column = getattr(self.model, query_filter.key)
            if query_filter.op == 'eq':
                query = query.filter(filter_column == query_filter.val)
            elif query_filter.op == 'lt':
                query = query.filter(filter_column < query_filter.val)
            elif query_filter.op == 'le':
                query = query.filter(filter_column <= query_filter.val)
            elif query_filter.op == 'gt':
                query = query.filter(filter_column > query_filter.val)
            elif query_filter.op == 'ge':
                query = query.filter(filter_column >= query_filter.val)
            elif query_filter.op == 'like':
                query = query.filter(filter_column.like(query_filter.val))
            elif query_filter.op == 'in':
                query = query.filter(filter_column.in_(query_filter.val))
            elif query_filter.op == 'between':
                query = query.filter(filter_column.between(*query_filter.val))

        return query

    @staticmethod
    def get_prev_link(params, paginate):
        prev_params = copy(params)
        prev_params['__page'] = paginate['__page'] - 1
        if prev_params['__page'] >= 1:
            return request.base_url + '?' + urllib.urlencode(prev_params)
        else:
            return None

    @staticmethod
    def get_next_link(params, paginate):
        prev_params = copy(params)
        prev_params['__page'] = paginate['__page'] + 1
        return request.base_url + '?' + urllib.urlencode(prev_params)

    def parse_params(self, params):
        processes = dict()
        paginate = dict()
        filters = []
        params.setdefault('__page', 1)
        params.setdefault('__page_size', self.default_page_size)
        for key, value in params.items():
            if key in self.PROCESSES:
                processes[key] = self.parse_process(key, value)
            elif key in self.PAGINATE:
                paginate[key] = self.parse_paginate(key, value)
            else:
                filters.append(self.parse_filter(key, value))

        return processes, filters, paginate

    def do_query(self, params, relation=None, pk=None):
        processes, filters, paginate = self.parse_params(params)
        show_query = self.get_show_query(processes.get('__show', []))
        if relation and pk is not None:
            rel_query = show_query.filter(getattr(self.model, relation.back_populates).any(id=pk))
            filter_query = self.filter_query(rel_query, filters)
        else:
            filter_query = self.filter_query(show_query, filters)
        paginate_query = self.paginate_query(
            filter_query, paginate['__page'], paginate['__page_size'])
        result = [query_result2dict(item) for item in paginate_query]

        return {
            'result': result,
            'page': paginate['__page'],
            'page_size': paginate['__page_size'],
            'prev_page': self.get_prev_link(params, paginate),
            'next_page': self.get_next_link(params, paginate)
        }


class RestQuery(object):

    def __init__(self, app, name, model):
        self.app = app
        self.name = name
        self.model = ModelWrapper(app=self.app, name=name, model=model)
        self.relations = inspect(model).relationships
        self.relation_models = self.init_relation_models()

    def init_relation_models(self):
        relation_models = dict()
        for rel_name, relation in self.relations.items():
            rel_table_name = relation.table.fullname
            relation_model = get_model_by_tablename(rel_table_name)
            relation_models[rel_name] = ModelWrapper(app=self.app, name=rel_table_name, model=relation_model)

        return relation_models

    def do_self_query(self, params):
        return self.model.do_query(params)

    def do_relation_query(self, params, rel_name, pk):
        relation = self.relations[rel_name]
        relation_model = self.relation_models[rel_name]
        return relation_model.do_query(params, relation, pk)

    def query(self, params):
        rel_name = params.pop('__relation', None)
        pk = params.pop('__pk', None)
        if rel_name and pk is not None:
            if rel_name not in self.relations:
                raise ValidationError(u'{0} is not a relation of {1}'.format(
                    rel_name, self.name))
            return self.do_relation_query(params, rel_name, pk)
        else:
            return self.do_self_query(params)

    def __call__(self, params):
        return self.query(params)


class RestModel(object):

    def __init__(self, app, name, model=None):
        self.app = app
        self.name = name
        self.model = model or get_model_by_tablename(name)
        self.rest_query = RestQuery(app=self.app, name=self.name, model=self.model)
        self._url_map = dict()

    @staticmethod
    def validate_keys(table_name, columns, keys):
        invalid_keys = frozenset(keys) - frozenset(columns)

        if invalid_keys:
            raise ValidationError(u'{0} is not attributes of {1}'.format(
                u','.join(invalid_keys), table_name))

        return True

    def http_get(self, params):
        return self.rest_query(params)

    def http_get_pk(self, params):
        item = self.model.get(params['id'])
        return item.to_dict() if item else rest_abort(404)

    def http_post(self, data):
        if data.pop('id', None):
            raise ValidationError(u"id can't be specified when post")

        self.validate_keys(self.name, self.model.get_column_names(), data.keys())
        item = self.model(**data)
        return item.save().to_dict()

    def http_delete(self, params):
        # if the item need to delete not exists,
        # return empty dict, else return the item dict

        item = self.model.get(params['id'])
        res = dict()
        if item:
            res = item.to_dict()
            item.delete()
        return res

    def http_put(self, data):
        _id = data.pop('id')
        self.validate_keys(self.name, self.model.get_column_names(), data.keys())

        if not self.model.get(_id):
            raise ValidationError(u'id {0} of {1} not exists'.format(_id, self.name))

        self.model.query_update(query={'id': _id}, data=data)
        return self.model.get(_id).to_dict()

    def init_bp(self, bp):
        bp.rest_route(rule=self.name, methods=['GET'])(
            self.http_get, '_'.join((self.name, self.http_get.__name__)))

        bp.rest_route(rule=self.name + '/<id>', methods=['GET'])(
            self.http_get_pk, '_'.join((self.name, self.http_get_pk.__name__)))

        bp.rest_route(rule=self.name + '/<id>', methods=['PUT'])(
            self.http_put, '_'.join((self.name, self.http_put.__name__)))

        bp.rest_route(rule=self.name, methods=['POST'])(
            self.http_post, '_'.join((self.name, self.http_post.__name__)))

        bp.rest_route(rule=self.name + '/<id>', methods=['DELETE'])(
            self.http_delete, '_'.join((self.name, self.http_delete.__name__)))

        bp.rest_route(rule=self.name + '/<__pk>/<__relation>', methods=['GET'])(
            self.http_get, '_'.join((self.name, self.http_get.__name__, 'relations'))
        )

        return bp
