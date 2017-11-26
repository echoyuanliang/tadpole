#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/5 by allen
"""

import socket
import logging
import logging.handlers as sys_handlers

from flask import request

import handlers as custom_handlers


class CustomFormatter(logging.Formatter):

    def format(self, record):
        try:
            setattr(record, 'url', request.url)
        except RuntimeError:
            setattr(record, 'url', 'Null')

        setattr(record, 'hostname', socket.gethostname())
        return logging.Formatter.format(self, record)


class AppLogger(object):

    def __init__(self, app):
        self._app = app
        self._default_formatter = self._app.config.get('LOG_FORMATTER')
        self._default_level = self._app.config.get('LOG_LEVEL', logging.INFO)

    def init_handler(self, handler_cls, config):
        formatter = config.pop('formatter', self._default_formatter)
        level = config.pop('level', self._default_level)
        handler = handler_cls(**config)
        if formatter:
            handler.setFormatter(CustomFormatter(formatter))
        handler.setLevel(level)
        self._app.logger.addHandler(handler)
        return handler

    @staticmethod
    def _get_handler_cls(handler_name):
        if not handler_name:
            raise Exception(u'logger handler is required')

        cls = getattr(logging, handler_name, None) or getattr(sys_handlers, handler_name, None) \
            or getattr(custom_handlers, handler_name, None)

        if cls and issubclass(cls, logging.Handler):
            return cls

        raise Exception(u'handler {0} is not support'.format(handler_name))

    def __call__(self, *args, **kwargs):
        for handler in self._app.logger.handlers:
            handler.setFormatter(CustomFormatter(self._default_formatter))

        for logger_name, logger_config in self._app.config['LOGGERS'].items():
            self._app.logger.debug(u'init logger {0}'.format(logger_name))

            if logger_config.pop('disable', None):
                continue

            handler_name = logger_config.pop('handler', None)
            handler_cls = self._get_handler_cls(handler_name)

            self.init_handler(handler_cls, logger_config)

        return self._app.logger


def init_logger(app):
    logger = AppLogger(app)()
    return logger
