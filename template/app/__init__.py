# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/5 by allen
"""

from flask import request, session
from app.lib.logger import init_logger


class Init(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, *args, **kwargs):
        self._app.logger.debug('init config')
        self.init_config()
        self._app.logger.debug('init logger')
        init_logger(self._app)
        self._app.logger.debug('init before')
        self.init_before()
        return self._app

    def init_config(self):
        self._app.config.from_object('config')
        self._app.config.from_pyfile('config.py')

    def init_before(self):
        @self._app.before_request
        def before_request():
            ip_list = request.headers.getlist("X-Forwarded-For")
            session['remote_address'] = ip_list[0].split(',')[0] if ip_list else request.remote_addr


def init_app(app):
    return Init(app)()
