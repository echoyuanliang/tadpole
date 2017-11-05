# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/5 by allen
"""

import time
from logging import Handler
from redis import StrictRedis, ConnectionPool


class RedisHandler(Handler):
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 6379
    DEFAULT_DB = 0
    DEFAULT_KEY = "logger"

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT,
                 db=DEFAULT_DB, key=DEFAULT_KEY,
                 date_cut=False, conn_pool=None):

        super(RedisHandler, self).__init__()

        self.host = host
        self.port = port
        self.db = db
        self.key = key
        self.date_cut = date_cut
        if conn_pool:
            self.conn_pool = conn_pool
        else:
            self.conn_pool = ConnectionPool(host=self.host, port=self.port, db=self.db)

        self.redis = StrictRedis(connection_pool=self.conn_pool)

    def _get_key(self):
        if not self.date_cut:
            return self.key
        else:
            return self.key + ":" + time.strftime("%Y-%m-%d")

    def emit(self, record):
        key = self._get_key()
        msg = self.format(record)
        self.redis.rpush(key, msg)
