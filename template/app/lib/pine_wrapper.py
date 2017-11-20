# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/18 by allen
"""

from functools import partial
from flask import Flask, Blueprint


class PineFlask(Flask):
    from app.lib.utils import CustomJsonEncoder

    json_encoder = CustomJsonEncoder

    def __init__(self, *args, **kwargs):
        from app.lib.rest_route import rest_route

        super(PineFlask, self).__init__(*args, **kwargs)
        self.rest_route = partial(rest_route, self)


class PineBlueprint(Blueprint):

    def __init__(self, *args, **kwargs):
        from app.lib.rest_route import rest_route

        super(PineBlueprint, self).__init__(*args, **kwargs)
        self.rest_route = partial(rest_route, self)

