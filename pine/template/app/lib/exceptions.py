# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/7 by allen
"""


class CustomError(Exception):

    def __init__(self, msg):
        super(CustomError, self).__init__(msg)
        self.msg = msg
        self.code = 500

    def to_dict(self):
        return dict(code=self.code, msg=self.msg)

    def __unicode__(self):
        return unicode(self.msg)

    def __str__(self):
        return str(self.msg)


class InternalError(CustomError):

    def __init__(self, msg):
        super(InternalError, self).__init__(msg)
        self.code = 500


class ValidationError(CustomError):

    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)
        self.code = 400


class SupportError(InternalError):
    def __init__(self, msg):
        super(SupportError, self).__init__(msg)
        self.code = 500


class AuthError(CustomError):

    def __init__(self, msg):
        super(AuthError, self).__init__(msg)
        self.code = 401


class PermissionError(CustomError):
    def __init__(self, msg):
        super(PermissionError, self).__init__(msg)
        self.code = 403


class RestHttpError(CustomError):

    _code_map = {
        400: 'bad request, please check your params ',
        401: 'authenticate failed, please check your token or password',
        403: 'permission denied, you has not permission access this resource',
        404: 'resource not found, please check your url',
        500: 'sorry, internal error happened',
        405: 'request method not allowed'
    }

    def __init__(self, code):
        msg = self._code_map[code]
        super(RestHttpError, self).__init__(msg)
        self.code = code
