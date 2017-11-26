#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/7 by allen
"""

from main import app


@app.rest_route("/health", methods=['GET', "HEAD"])
def health_check(data):
    return dict(code=200, message="I'm OK!!!", data=data)
