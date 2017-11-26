#!/usr/bin/env python
# coding: utf-8

"""
    create at 2017/11/2 by allen
"""

import logging
from logging import StreamHandler, INFO
from termcolor import colored


_logger = logging.getLogger(__name__)
_logger.setLevel(INFO)
_logger.addHandler(StreamHandler())


def waring(msg):
    return _logger.warning(colored(msg, "yellow"))


def error(msg):
    return _logger.error(colored(msg, "red"))


def debug(msg):
    return _logger.debug(colored(msg, "green"))


def info(msg):
    return _logger.info(colored(msg, "green"))


def set_level(level):
    return _logger.setLevel(level)
