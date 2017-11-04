# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/4 by allen
"""

TEMPLATE_SRC = 'template/'
TEMPLATE_HEADER = "# !/usr/bin/python\n# coding: utf-8\n"
TEMPLATE_DIRS_CREATE = ('data/', 'logs/', 'instance/')
TEMPLATE_CONF_NAME = "config.py"
TEMPLATE_GUN_CONF = "gun.py"

# project config, render to config.py
TEMPLATE_PROJECT = {
    'VERSION': "v0.0.1",
    'OWNER': "pine",
    'DEBUG': True,
    'EMAIL': '',
}

# gunicorn config, render to gun.py
TEMPLATE_GUNICORN = {
    "bind": "0.0.0.0:8080",
    "workers": "2*cpu",
    "worker_class": "sync",
    "backlog": 2048,
    "daemon": True,
    "loglevel": "info",
    "accesslog": 'logs/access.log',
    "errorlog": 'logs/error.log',
    "access_log_format": "%({X-Real-IP}i)s %(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
}
