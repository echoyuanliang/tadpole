#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/7 by allen
"""

import json
import decimal
from datetime import datetime, date
from collections import Mapping, Iterable
from urlparse import urljoin
from flask import Flask, request
from exceptions import RestHttpError


class CustomJsonEncoder(json.JSONEncoder):

    DATETIME_FMT = "%Y-%m-%d %H:%M:%S"

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.strftime(self.DATETIME_FMT)
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, Mapping):
            return dict(obj)
        elif isinstance(obj, Iterable):
            return list(obj)

        to_dict = getattr(obj, '_as_dict', None) or getattr(obj, 'to_dict', None)
        if to_dict and callable(to_dict):
            return to_dict()

        return super(CustomJsonEncoder, self).default(obj)


def flask_res(data=None, code=200):
    data = dict(msg='ok', code=200) if not data else data
    return Flask.response_class(json.dumps(data, cls=CustomJsonEncoder), status=code, mimetype='application/json')


def rest_abort(code):
    raise RestHttpError(code)


def get_bp_prefix(app, bp_name):
    prefix_pattern = app.config.get('BP_PREFIX_PATTERN', '/api/{0}/{1}/')
    default_prefix = prefix_pattern.format(app.config['VERSION'], bp_name)
    if not app.config.get('BP_PREFIX', None):
        app.config['BP_PREFIX'] = dict()
    app.config['BP_PREFIX'].setdefault(bp_name, default_prefix)
    return app.config['BP_PREFIX'][bp_name]


def get_relation_url(table_name, pk, relation_name):
    from main import app
    bp_prefix = get_bp_prefix(app, 'rest_db')
    relation_path = '/'.join((table_name, str(pk), relation_name))
    return urljoin(urljoin(request.host_url, bp_prefix),  relation_path)
