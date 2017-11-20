# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/16 by allen
"""

from redis import Redis, ConnectionPool


class RedisManager(Redis):

    def __init__(self, *args, **kwargs):
        super(RedisManager, self).__init__(*args, **kwargs)
        self.connection_conf = {
            'host': 'localhost',
            'port': 6379
        }

        self.connection_pool = None

    def init_app(self, app):
        self.connection_conf = app.config.get('REDIS_CONFIG', self.connection_conf)
        self.connection_pool = ConnectionPool(**self.connection_conf)


extension = RedisManager()
