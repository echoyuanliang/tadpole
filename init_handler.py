# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/2 by allen
"""

import os
import shutil

import logger


class _InitHandler(object):

    TEMPLATE_DIR = 'template/'

    def __init__(self, project_name, version, author, email):
        self.project_name = project_name
        self.version = version
        self.author = author
        self.email = email
        self.work_dir = os.path.join(os.getcwd(), self.project_name)
        self.cur_dir = os.path.dirname(os.path.realpath(__file__))
        self.template_dir = os.path.join(self.cur_dir, self.TEMPLATE_DIR)

    def _move_files(self):
        logger.debug("copy from {0} to {1}".format(self.template_dir, self.work_dir))
        shutil.copytree(self.template_dir, self.work_dir)

    def __call__(self, *args, **kwargs):
        self._move_files()
        os.chdir(self.work_dir)


def do_init(project_name, version, author, email):
    handler = _InitHandler(project_name, version, author, email)
    return handler()
