# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/2 by allen
"""

import os
import json
import codecs
import shutil
from copy import deepcopy

import logger
import config


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
    def _make_instance():
        instance_config = "instance/{0}".format(config.TEMPLATE_CONF_NAME)
        logger.debug("make instance config {0}".format(instance_config))
        if "instance/" in config.TEMPLATE_DIRS_CREATE:
            with open(instance_config, "w") as ifp:
                ifp.write(config.TEMPLATE_HEADER)

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

        logger.debug("make config {0}".format(config.TEMPLATE_CONF_NAME))
        config_dict = self._get_project_config()
        config_content = self.render_config(config_dict, fmt_dict=self.fmt_dict)
        with codecs.open(config.TEMPLATE_CONF_NAME, "w", "utf-8") as cfp:
            cfp.write(config_content)

        logger.debug("make config {0}".format(config.TEMPLATE_GUN_CONF))
        config_content = self.render_config(config.TEMPLATE_GUNICORN, {
            'workers': self._process_gun_workers})
        with codecs.open(config.TEMPLATE_GUN_CONF, "w", "utf-8") as gfp:
            gfp.write(config_content)

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

# for test
if __name__ == '__main__':
    import time
    do_init('data/test{0}'.format(int(time.time())), 'v0.1.1', 'pine', '')
