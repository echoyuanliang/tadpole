# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/7 by allen
"""

import json
import datetime
import decimal
from flask import Flask
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


def flask_res(data=None, status=200):
    data = dict(msg='ok', code=200) if not data else data
    return Flask.response_class(json.dumps(data, cls=CustomJsonEncoder), status=status, mimetype='application/json')


def rest_abort(code):
    raise RestHttpError(code)
