# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/22 by allen
"""

import re
from flask import request, session, current_app
from app.lib.constant import ResourceType
from app.models.auth import Resource, role_resource, Role, user_role, User
from app.lib.exceptions import AuthError, PermissionError


class HttpBasicAuth(object):

    def __init__(self, user_loader, hash_password_handler=None,
                 verify_password_handler=None):

        self.user_loader = user_loader
        self.hash_password_handler = hash_password_handler
        self.verify_password_handler = verify_password_handler

    def hash_password(self, auth):
        if self.hash_password_handler:
            try:
                return self.hash_password_handler(auth.password)
            except Exception as e:
                current_app.logger.exception(str(e))

            try:
                return self.hash_password_handler(auth.username, auth.password)
            except Exception as e:
                current_app.logger.exception(str(e))

        return auth.passsword

    def get_user(self, auth):
        if not auth or not auth.username:
            return None

        user = self.user_loader(auth.username)

        return user

    def auth_user(self, auth):
        if session.get('user_id'):
            return self.user_loader(session['user_id'])

        user = self.get_user(auth)
        stored_password = user.password if user else None
        if not stored_password:
            return None

        if self.verify_password_handler:
            return self.verify_password_handler(auth.username, auth.password)

        client_password = self.hash_password(auth)
        if stored_password == client_password:
            session['user_id'] = user.id
            return user

        return None

    def __call__(self, auth):
        return self.auth_user(auth=auth)


class AuthBase(object):

    @staticmethod
    def get_user_resources(user_id):
        raise NotImplemented

    @staticmethod
    def load_user(account):
        raise NotImplemented

    @staticmethod
    def get_user_resources(user_id):
        raise NotImplemented

    @staticmethod
    def load_resources(rtype, name, operation):
        raise NotImplemented


class AuthDbLoader(AuthBase):

    @staticmethod
    def get_user_resources(user_id):
        return Resource.query.join(role_resource, Role, user_role, User). \
            filter(User.id == user_id)

    @staticmethod
    def load_user(account):
        return User.get_by(account=account).first()

    @staticmethod
    def get_user_resources(user_id):
        return Resource.query.join(role_resource, Role, user_role, User). \
            filter(User.id == user_id)

    @staticmethod
    def load_resources(rtype, name, operation):
        http_resources = Resource.get_by(rtype=rtype, operation=operation)

        return [resource for resource in http_resources
                if re.match(resource.name, name)]


class PermissionAuth(object):

    def __init__(self, auth_handler, auth_info_loader):
        self.auth_info_loader = auth_info_loader if auth_info_loader \
            else AuthDbLoader()

        self.auth_handler = auth_handler if auth_handler else \
            HttpBasicAuth(user_loader=auth_info_loader.load_user)

    def validate_user_permission(self, user, resources):
        user_resources = set(resource.id for
                             resource in self.auth_info_loader.get_user_resources(user.id))

        access_resources = set(resource.id for resource in resources)

        if access_resources.issubset(user_resources):
            return True

    def validate_request_permission(self):
        path_resources = self.auth_info_loader.load_resources(
            ResourceType.HTTP, request.path, request.method.upper())
        if not path_resources:
            return True
        user = self.auth_handler(request.authorization)
        if not user:
            raise AuthError(u'authenticate failed, please check your username or password')

        if not self.validate_user_permission(user, path_resources):
            raise PermissionError(u'permission denied, your  have not permission to do {0} on {1}'.format(
                request.path, request.method.upper()))
