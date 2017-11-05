# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/4 by allen
"""


from flask import Flask
from app import init_app

app = Flask(__name__, instance_relative_config=True)

with app.app_context():
    app = init_app(app)

if __name__ == '__main__':
    app.logger.info("app start")
    app.run(debug=True)

