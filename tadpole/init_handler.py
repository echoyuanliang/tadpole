# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/2 by allen
"""

import codecs
import json
import os
import shutil
import time
from copy import deepcopy
from subprocess import check_output

from tadpole import config
from tadpole import logger


class _PyConfigMixin(object):
    def __init__(self):
        pass

    @staticmethod
    def process_custom_config(config_dict, custom_processes):
        config_lines, import_lines = list(), list()
        
        if custom_processes:
            for key in set(custom_processes).intersection(set(config_dict.keys())):
                custom_imports, custom_config = custom_processes[key](key, config_dict.pop(key))
                import_lines.extend(custom_imports)
                config_lines.extend(custom_config)

        return config_dict, import_lines, config_lines

    @staticmethod
    def replace_fmt(config_content, fmt_dict):
        for key in fmt_dict:
            fmt_key = "{%s}" % key
            if fmt_key in config_content:
                config_content = config_content.replace(fmt_key, fmt_dict[key])

        return config_content

    @staticmethod
    def process_key_value(key, value):
        if isinstance(value, unicode):
            return u"{key} = u'{value}'\n".format(key=key, value=value)
        if isinstance(value, basestring):
            return u"{key} = '{value}'\n".format(key=key, value=value)
        elif isinstance(value, (list, dict)):
            return u"{key} = {value}\n".format(
                key=key, value=json.dumps(value, indent=4, ensure_ascii=False))

        return u"{key} = {value}\n".format(key=key, value=value)

    def render_config(self, config_dict, custom_processes=None, fmt_dict=None):

        config_dict = deepcopy(config_dict)
        config_dict, import_lines, config_lines = self.process_custom_config(
            config_dict, custom_processes)

        keys = config_dict['__KEYS_ORDER'] if config_dict.get('__KEYS_ORDER') else config_dict.keys()

        for key in keys:
            if key == '\n':
                config_lines.append(key)
                continue
            elif key not in config_dict or key.startswith('__'):
                continue
            line = self.process_key_value(key, config_dict[key])
            config_lines.append(line)

        config_content = u"{headers}\n{import_lines}\n{config_lines}".format(
            headers=config.TEMPLATE_HEADER, import_lines=u''.join(import_lines),
            config_lines=u''.join(config_lines))

        if fmt_dict:
            config_content = self.replace_fmt(config_content, fmt_dict)

        return config_content


class _InitHandler(_PyConfigMixin):

    def __init__(self, project_name, version, owner, email):

        super(_InitHandler, self).__init__()

        self.project_name = project_name
        self.version = version
        self.owner = owner
        self.email = email
        self.work_dir = os.path.join(os.getcwd(), self.project_name)
        self.cur_dir = os.path.dirname(os.path.realpath(__file__))
        self.template_dir = os.path.join(self.cur_dir, config.TEMPLATE_SRC)
        self.fmt_dict = {
            'app_name': self.project_name.lower(),
            'version': self.version.lower(),
            'owner': self.owner.lower(),
            'email': self.email
        }

    @staticmethod
    def _make_dirs():
        directories = config.TEMPLATE_DIRS_CREATE
        logger.debug(u"make dirs {0}".format(u','.join(directories)))

        for directory in directories:
            if not os.path.exists(directory):
                os.mkdir(directory)

    @staticmethod
    def _process_gun_workers(key, workers):
        import_lines, config_lines = list(), list()

        if isinstance(workers, int) or (
                    isinstance(workers, basestring) and workers.isdigit()):
            config_lines.append('{0} = {1}\n'.format(key, workers))
        else:
            try:
                wp_cpu = int(workers.split("*")[0])
            except Exception as e:
                logger.debug(str(e))
                wp_cpu = 2

            if wp_cpu < 1 or wp_cpu > 10:
                wp_cpu = 2

            import_lines.append("import multiprocessing\n")
            config_lines.append("{0} = multiprocessing.cpu_count() * {1} \n".format(key, wp_cpu))

        return import_lines, config_lines

    def _get_project_config(self):
        config_dict = deepcopy(config.TEMPLATE_PROJECT)
        config_dict.update({
            'APP_NAME': self.project_name,
            'VERSION': self.version,
            'OWNER': self.owner,
            'EMAIL': self.email
        })

        return config_dict

    def _init_config(self):

        # init config.py
        logger.debug("make config {0}".format(config.TEMPLATE_CONF_NAME))
        config_dict = self._get_project_config()
        config_content = self.render_config(config_dict, fmt_dict=self.fmt_dict)
        with codecs.open(config.TEMPLATE_CONF_NAME, "w", "utf-8") as cfp:
            cfp.write(config_content)

        # init instance/config.py
        instance_config = "instance/{0}".format(config.TEMPLATE_CONF_NAME)
        logger.debug("make instance config {0}".format(instance_config))
        if "instance/" in config.TEMPLATE_DIRS_CREATE:
            instance_dict = config.TEMPLATE_INSTANCE
            config_content = self.render_config(instance_dict)
            with codecs.open(instance_config, "w", "utf-8") as ifp:
                ifp.write(config_content)

        # init gun.py
        logger.debug("make config {0}".format(config.TEMPLATE_GUN_CONF))
        config_content = self.render_config(config.TEMPLATE_GUNICORN, {
            'workers': self._process_gun_workers})
        with codecs.open(config.TEMPLATE_GUN_CONF, "w", "utf-8") as gfp:
            gfp.write(config_content)

    def _process_template(self):
        logger.debug("gen %s file for start, stop ... actions" % self.project_name)
        with codecs.open("template.py", "r", "utf-8") as tfp:
            content = tfp.read()

        with codecs.open(self.project_name, "w", "utf-8") as pfp:
            content = content.replace("{{template}}", self.project_name)
            pfp.write(content)

        os.chmod(self.project_name, 0740)
        os.remove("template.py")

    @staticmethod
    def _init_venv():
        logger.debug("make venv")
        out = check_output("virtualenv --no-site-packages venv", shell=True)
        logger.debug(out)
        out = check_output("source venv/bin/activate && pip install -r requirements.txt",
                           shell=True)
        logger.debug(out)
        return True

    def _init_git(self):
        logger.debug("init git")
        try:
            out = check_output("git init && git add . && git commit -m 'init {0}'".
                               format(self.project_name), shell=True)
            logger.debug(out)
        except Exception as e:
            logger.debug(str(e))
            logger.info("git not found, git init ignore")

    def _init_projects(self):
        time_start = time.time()
        logger.info("init project {0}".format(self.project_name))
        logger.debug("copy from {0} to {1}".format(self.template_dir, self.work_dir))
        shutil.copytree(self.template_dir, self.work_dir)
        os.chdir(self.work_dir)
        self._make_dirs()
        self._init_config()
        self._process_template()
        self._init_venv()
        self._init_git()
        logger.info("init project success using %.3f seconds !!!" % (time.time() - time_start))

    def __call__(self, *args, **kwargs):
        self._init_projects()


def do_init(project_name, version, owner, email):
    handler = _InitHandler(project_name, version, owner, email)
    return handler()

# for test
if __name__ == '__main__':
    do_init('data/test{0}'.format(int(time.time())), 'v0.1.1', 'pine', '')
