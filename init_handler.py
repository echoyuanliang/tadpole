# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/2 by allen
"""

import os
import shutil

import logger
import config


class _InitHandler(object):

    def __init__(self, project_name, version, owner, email):
        self.project_name = project_name
        self.version = version
        self.owner = owner
        self.email = email
        self.work_dir = os.path.join(os.getcwd(), self.project_name)
        self.cur_dir = os.path.dirname(os.path.realpath(__file__))
        self.template_dir = os.path.join(self.cur_dir, config.TEMPLATE_SRC)

    @staticmethod
    def _make_dirs():
        directories = config.TEMPLATE_DIRS_CREATE
        logger.debug(u"make dirs {0}".format(u','.join(directories)))

        for directory in directories:
            if not os.path.exists(directory):
                os.mkdir(directory)

    @staticmethod
    def _make_instance():
        instance_config = "instance/{0}".format(config.TEMPLATE_CONFIG)
        logger.debug("make instance config {0}".format(instance_config))
        if "instance/" in config.TEMPLATE_DIRS_CREATE:
            with open(instance_config, "w") as ifp:
                ifp.write(config.TEMPLATE_HEADER)

    def _init_config(self):

        logger.debug("make config {0}".format(config.TEMPLATE_CONFIG))

        with open("config_template.py", "r") as cfp:
            config_template = cfp.read()

        config_content = config_template.format(
            app_name=self.project_name, version=self.version,
            owner=self.owner, email=self.email)

        with open(config.TEMPLATE_CONFIG, "w") as cfp:
            cfp.write(config_content)

        os.remove("config_template.py")

    def _init_manager(self):
        logger.debug("make project manager {0}".format(self.project_name))

        with open("init.sh", "r") as ifp:
            init_content = ifp.read()

        init_target = init_content.replace("pine", self.project_name, 1)

        with open(self.project_name, "w") as mfp:
            mfp.write(init_target)

        os.chmod(self.project_name, 0744)
        os.remove("init.sh")

    def _init_projects(self):
        logger.debug("copy from {0} to {1}".format(self.template_dir, self.work_dir))
        shutil.copytree(self.template_dir, self.work_dir)
        os.chdir(self.work_dir)
        self._make_dirs()
        self._make_instance()
        self._init_config()
        self._init_manager()

    def __call__(self, *args, **kwargs):
        self._init_projects()


def do_init(project_name, version, owner, email):
    handler = _InitHandler(project_name, version, owner, email)
    return handler()
