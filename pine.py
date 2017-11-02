# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/2 by allen
"""

import os
import shutil
from logging import DEBUG

import click
import logger

import project_default
from init_handler import do_init

VERSION = "0.1.1"
PROJECT_TEMPLATE = "template"


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(VERSION)
    ctx.exit()


def open_debug(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    logger.set_level(DEBUG)
    logger.debug('debug mod opened')


@click.group()
@click.option('-v', '--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
def cli():
    pass


def make_files(project_dir):
    logger.debug(os.path.abspath(os.curdir))
    shutil.copytree(PROJECT_TEMPLATE, project_dir)


@cli.command()
@click.option('-d', '--debug', is_flag=True, callback=open_debug,
              expose_value=False, is_eager=True)
@click.option('-n', '--project_name', prompt=True)
@click.option('-v', '--version', default=project_default.VERSION)
@click.option('-a', '--author', default=project_default.AUTHOR)
@click.option('-e', '--project_email', default=project_default.EMAIL)
def init(project_name, version, author, project_email):
    logger.debug("raw input project: {0}, version {1}, author: {2}, email: {3}".format(
        project_name, version, author, project_email
    ))

    do_init(project_name, version, author, project_name)


if __name__ == '__main__':
    cli()

