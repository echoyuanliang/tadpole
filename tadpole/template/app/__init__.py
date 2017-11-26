#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/5 by allen
"""

from flask import request, session
from sqlalchemy.exc import SQLAlchemyError

from app.lib.logger import init_logger
from app.lib.utils import flask_res
from app.lib.exceptions import CustomError
from app.lib.pine_wrapper import PineBlueprint
from app.lib.rest_model import RestModel
from app.lib.utils import get_bp_prefix
from app.lib.auth import PermissionAuth


class Init(object):
    def __init__(self, app, bp_list=None):
        self._app = app
        self._bp_list = bp_list or []
        self.permission_auth_handler = PermissionAuth()

    def __call__(self, *args, **kwargs):
        self.init_config()
        self.init_logger()
        self.init_before()
        self.init_views()
        self.init_extensions()
        self.init_error_handler()
        self.init_after()
        self.init_rest_db()
        return self._app

    def init_logger(self):
        self._app.logger.debug('init logger')
        init_logger(self._app)

    def init_config(self):
        self._app.logger.debug('init config')
        self._app.config.from_object('config')
        self._app.config.from_pyfile('config.py')

    def init_before(self):
        self._app.logger.debug('init before_request')

        @self._app.before_request
        def before_request():
            ip_list = request.headers.getlist("X-Forwarded-For")
            session['remote_address'] = ip_list[0].split(',')[0] if ip_list else request.remote_addr
            self.permission_auth_handler.validate_request_permission()

    def init_after(self):
        self._app.logger.debug('init after_request')

        @self._app.after_request
        def after_request(response):
            response.headers['Server'] = self._app.config['APP_NAME']
            return response

    def init_error_handler(self):
        self._app.logger.debug("init error handler")

        @self._app.errorhandler(CustomError)
        def handler_custom_error(error):
            return flask_res(data=error, code=error.code)

        @self._app.errorhandler(SQLAlchemyError)
        def handler_db_error(error):
            msg = u'DB操作失败: {0}'.format(str(error))
            self._app.logger.exception(msg)
            data = {'code': 500, 'msg': msg}
            return flask_res(data=data, code=500)

    def init_extensions(self):
        from app import extensions
        self._app.logger.debug("init extensions")
        module_priority_chain = getattr(extensions, 'module_priority_chain', [])

        for name in module_priority_chain:
            try:
                _module = __import__('{0}.{1}'.format(extensions.__name__, name), fromlist=[''])
                if hasattr(_module, 'init_app'):
                    init_fn = getattr(_module, 'init_app', None)
                elif hasattr(_module, 'extension'):
                    init_fn = getattr(_module.extension, 'init_app', None)
                if not init_fn:
                    raise Exception(u'init_app of {0} is not defined'.format(name))
                elif not callable(init_fn):
                    raise Exception(u'init_app of {0} is not callable'.format(name))

                init_fn(self._app)
            except ImportError as e:
                self._app.logger.exception(str(e))

    def register_bp(self, bp):
        bp_prefix = get_bp_prefix(self._app, bp.name)
        self._app.register_blueprint(bp, url_prefix=bp_prefix)

    def init_views(self):
        import views

        self._app.logger.debug("init views")

        for bp in self._bp_list:
            self.register_bp(bp)

    def init_rest_db(self):
        from app import models
        from app.lib.database import get_model_registry

        if not self._app.config.get('REST_DB'):
            self._app.logger.debug("ignore init rest_db")
            return True

        self._app.logger.debug("init rest_db")
        rest_db = PineBlueprint('rest_db', __name__)

        rest_models = (RestModel(self._app, model.__tablename__, model)
                       for model in get_model_registry())

        for rest_model in rest_models:
            rest_model.init_bp(bp=rest_db)

        self.register_bp(rest_db)

        return True


def init_app(app, bp_list):
    with app.app_context():
        return Init(app, bp_list)()
