#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/7 by allen
"""

from copy import deepcopy
from functools import wraps
from flask import request, Flask, Response, current_app
from app.lib.utils import flask_res
from app.lib.validator import Validator


class RestRoute(object):

    def __init__(self, bp, rule="", methods=None, validator=None,
                 pre_processes=None):
        self.rule = rule
        self.methods = methods or ['GET']
        self.validator = Validator(validator) if validator else None
        self.pre_processes = pre_processes or []
        self.bp = bp

    def __call__(self, view_function, endpoint=None):
        view_endpoint = endpoint or view_function.__name__

        @self.bp.route(rule=self.rule, methods=self.methods, endpoint=view_endpoint)
        @wraps(view_function)
        def wrapped(**kwargs):
            data = deepcopy(kwargs)
            http_data = self.get_http_data()
            data.update(http_data)
            self.pre_process(data)
            self.result = view_function(data)
            return self.post_process(self.result)

        return wrapped

    def pre_process(self, data):
        if self.validator:
            self.validator(data)

        for process in self.pre_processes:
            process(data)

    @staticmethod
    def post_process(result):
        if isinstance(result, (Response, Flask.response_class)):
            # 用户已经封装好返回值
            return result
        else:
            return flask_res({
                'code': 200,
                'msg': 'ok',
                'result': result
            })

    @staticmethod
    def get_http_data():
        http_data = dict()
        http_data.update(request.args.to_dict())
        try:
            http_data.update(request.json)
        except Exception as e:
            current_app.logger.info(u'no json data {0}'.format(str(e)))

        return http_data


def rest_route(bp, rule="", methods=None, validator=None, pre_processes=None):
    return RestRoute(bp, rule, methods, validator, pre_processes)
