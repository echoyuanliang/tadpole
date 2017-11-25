# !/usr/bin/env python
# chkconfig: - 30 74
# description:  This is a daemon which handles app

"""
    create at 2017/11/24 by allen
"""

import os
import sys
import imp
import time
import signal
from subprocess import check_output, CalledProcessError

SERVICE_NAME = "{{template}}"
WORK_DIR = os.path.curdir
DEBUG = False
GUN_CONF = "gun.py"
APP = "main:app"
STOP_WAIT = 5
START_WAIT = 20
Red = '\033[0;31m'
Green = '\033[0;32m'
Yellow = '\033[0;33m'
Color_Off = '\033[0m'


def log_error(msg):
    print(Red + msg + Color_Off)


def log_info(msg):
    print(Green + msg + Color_Off)


def log_debug(msg):
    if DEBUG:
        print(Yellow + msg + Color_Off)


def log_fatal(msg):
    log_error(msg)
    exit(-1)


def get_gun_module():
    try:
        _gun = imp.load_source("gun", GUN_CONF)
        return _gun
    except Exception as e:
        log_fatal("file {0} must exists, current error {1}".format(GUN_CONF, str(e)))


gun = get_gun_module()


def get_pidfile_path():
    try:
        return gun.pidfile
    except Exception as e:
        log_fatal("file {0} must exists and has pidfile conf item, current error: {1}".
                  format(GUN_CONF, str(e)))

pid_file = get_pidfile_path()


def execute_cmd(cmd):
    try:
        out = check_output(cmd, shell=True)
        return True, out
    except CalledProcessError as e:
        log_debug("execute {0} failed, {1}".format(cmd, str(e)))
        return False, e.message


def read_pid():
    try:
        with open(pid_file, 'r') as pfp:
            return int(pfp.read())
    except Exception as e:
        log_debug(str(e))
        return -1


def get_pid_sub(pid):
    ps_cmd = "ps -eo ppid,pid,start | grep {0}".format(pid)
    ps_status, ps_output = execute_cmd(ps_cmd)
    if not ps_status:
        return None, None

    master = ()
    workers = []
    for line in ps_output.splitlines():
        cur_ppid, cur_pid, cur_start = line.split()
        proc = (int(cur_pid), cur_start)
        if proc[0] == pid:
            master = proc
        else:
            workers.append(proc)

    return master, workers


def do_status():
    pid = read_pid()
    if pid < 0:
        log_info("service {0} stopped".format(SERVICE_NAME))
        return False

    master, workers = get_pid_sub(pid)
    if not master or not workers:
        log_info("service {0} stopped".format(SERVICE_NAME))
        return False

    log_info("master process pid: {master_id}, started at {master_started};".format(
        master_id=pid, master_started=master[1]))
    log_info("worker process count: %d" % len(workers))

    for worker in sorted(workers):
        log_info("pid {0}, started at {1};".format(worker[0], worker[1]))

    return True


def service_alive():
    pid = read_pid()
    if pid < 0:
        return False

    master, workers = get_pid_sub(pid)
    if master or workers:
        return True

    return False


def clear_pidfile():
    try:
        os.remove(pid_file)
    except Exception as e:
        log_debug(str(e))
        pass


def do_start():

    start_time = time.time()
    if service_alive():
        log_fatal("service {0} has been started, can't be start twice".format(SERVICE_NAME))

    clear_pidfile()
    gun_cmd = "venv/bin/python venv/bin/gunicorn -c {0} {1}".format(GUN_CONF, APP)
    status, output = execute_cmd(gun_cmd)
    if not status:
        log_fatal("execute {0} failed, start {1} failed".format(gun_cmd, SERVICE_NAME))

    if not wait_start():
        log_fatal("wait start  %s  for %.3f seconds failed" % (SERVICE_NAME, time.time() - start_time))

    if not do_status():
        log_fatal("start {0} failed".format(SERVICE_NAME))

    log_info("start %s success using %.3f seconds" % (SERVICE_NAME, time.time() - start_time))
    return True


def kill_process(pid, sig):
    try:
        os.kill(pid, sig)
    except Exception as e:
        log_debug('kill {0} failed, {1}'.format(pid, str(e)))
        return False

    return True


def wait_start():
    return wait_status(START_WAIT, True)


def wait_stop():
    return wait_status(STOP_WAIT, False)


def wait_status(wait_seconds, alive):
    wait_secs = 0
    while wait_secs <= wait_seconds:

        if service_alive() == alive:
            return True

        time.sleep(.1)

    return service_alive() == alive


def do_stop():
    start_time = time.time()

    if not service_alive():
        clear_pidfile()
        log_info("service {0} has been stopped".format(SERVICE_NAME))
        return True

    pid = read_pid()
    if not kill_process(pid, signal.SIGTERM):  # graceful stop
        log_fatal("kill process {0} failed, stop {1} failed".format(pid, SERVICE_NAME))

    if not wait_stop():
        kill_process(read_pid(), signal.SIGQUIT)  # quick stop

    if not wait_stop():
        log_fatal("pid file {0}  still exists, stop {1} failed".format(
            pid_file, SERVICE_NAME))

    # pid file removed
    master, workers = get_pid_sub(pid)
    if master or workers:
        processes = workers.append(master)
        log_fatal('process {0} still exists, stop {1}  failed'.format(
            ','.join([proc[0] for proc in processes]), SERVICE_NAME))

    log_info("stop %s success using %.3f seconds" % (SERVICE_NAME, time.time() - start_time))
    return True


def do_reload():
    start_time = time.time()

    if not service_alive():
        log_info("service {0} has been stopped, start service.".format(SERVICE_NAME))
        return do_start()

    pid = read_pid()
    if not kill_process(pid, signal.SIGHUP):
        log_fatal("reload {0} failed".format(SERVICE_NAME))

    time.sleep(.5)

    if not do_status():
        log_fatal("reload {0} failed".format(SERVICE_NAME))

    log_info("reload %s success using %.3f seconds" % (SERVICE_NAME, time.time() - start_time))


def do_help():
    help_map = {
        'status': 'show status of service {0}'.format(SERVICE_NAME),
        'start': 'start service {0}'.format(SERVICE_NAME),
        'stop': 'stop service {0}'.format(SERVICE_NAME),
        'reload': 'reload config of service {0}, if not started, do start'.format(SERVICE_NAME),
        'help': 'show usage of this script'
    }

    for key, value in help_map.items():
        log_info("{0}: {1}".format(key, value))

    exit(0)


if __name__ == '__main__':
    action_map = {
        'status': do_status,
        'start': do_start,
        'stop': do_stop,
        'reload': do_reload,
        'help': do_help
    }

    if len(sys.argv) == 1:
        action = 'help'
    else:
        action = sys.argv[1]

    if action not in action_map:
        do_help()

    action_map[action]()
    exit(0)
