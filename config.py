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
TEMPLATE_LOG_FORMAT = '%(hostname)s %(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s '

TEMPLATE_PROJECT = {
    '__KEYS_ORDER': ['APP_NAME', 'VERSION', 'OWNER', 'EMAIL', 'DEBUG', '\n',
                     'LOG_FORMATTER', 'LOGGERS'],

    'VERSION': "v0.0.1",
    'OWNER': "pine",
    'DEBUG': True,
    'EMAIL': '',
    'LOG_FORMATTER': TEMPLATE_LOG_FORMAT,
    'LOGGERS': {
        'error_log': {
            'handler': 'RotatingFileHandler',
            'level': 'ERROR',
            'formatter': TEMPLATE_LOG_FORMAT,
            'filename': 'logs/error.log',
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 7,
            'encoding': 'utf-8'
        },

        'app_log': {
            'handler': 'RotatingFileHandler',
            'level': 'INFO',
            'formatter': TEMPLATE_LOG_FORMAT,
            'filename': 'logs/app.log',
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 7,
            'encoding': 'utf-8'
        },

        'mail_log': {
            'handler': 'SMTPHandler',
            'level': 'ERROR',
            'formatter': TEMPLATE_LOG_FORMAT,
            'fromaddr': 'error@{app_name}.com',
            'toaddrs': ['{email}'],
            'mailhost': 'smtp.{app_name}.com',
            'disable': 1,  # # use number for boolean, compatible with json
        },

        "redis_log": {
            "handler": "RedisHandler",
            "host": "127.0.0.1",
            "port": 6379,
            "date_cut": 1,
            "db": 0,
            "key": "{app_name}:log",
            "level": "INFO",
            "disable": 1
        }

    }
}

# gunicorn config, render to gun.py
TEMPLATE_GUNICORN = {
    "__KEYS_ORDER": ['bind', 'workers', 'worker_class', 'backlog', 'daemon',
                     'loglevel', 'accesslog', 'errorlog', 'access_log_format'],

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
