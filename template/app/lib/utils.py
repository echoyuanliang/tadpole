# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/7 by allen
"""

import json
import datetime
import decimal
from urlparse import urljoin
from flask import Flask, request
from exceptions import RestHttpError


class CustomJsonEncoder(json.JSONEncoder):

    DATE_FMT = "%Y-%m-%d"
    DATETIME_FMT = "%Y-%m-%d %H:%M:%S"

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime(self.DATE_FMT)
        elif isinstance(obj, datetime.date):
            return obj.strftime(self.DATETIME_FMT)
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif callable(getattr(obj, '_as_dict', None)):  # for namedtuple, sqlalchemy result
            return getattr(obj, '_as_dict')()
        elif callable(getattr(obj, 'to_dict', None)):
            return getattr(obj, 'to_dict')()
        elif isinstance(obj, dict):  # for OrderedDict ,defaultdict
            return dict(obj)
        elif isinstance(obj, (set, tuple)):
            return list(obj)
        else:
            return super(CustomJsonEncoder, self).default(obj)


def flask_res(data=None, code=200):
    data = dict(msg='ok', code=200) if not data else data
    return Flask.response_class(json.dumps(data, cls=CustomJsonEncoder), status=code, mimetype='application/json')


def rest_abort(code):
    raise RestHttpError(code)


def get_bp_prefix(app, bp_name):
    prefix_pattern = app.config.get('BP_PREFIX_PATTERN', '/{0}/{1}/')
    default_prefix = prefix_pattern.format(bp_name, app.config['VERSION'])
    if not app.config.get('BP_PREFIX', None):
        app.config['BP_PREFIX'] = dict()
    app.config['BP_PREFIX'].setdefault(bp_name, default_prefix)
    return app.config['BP_PREFIX'][bp_name]


def get_relation_url(table_name, pk, relation_name):
    from main import app
    bp_prefix = get_bp_prefix(app, 'rest_db')
    relation_path = '/'.join((table_name, str(pk), relation_name))
    return urljoin(urljoin(request.host_url, bp_prefix),  relation_path)
