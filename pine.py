# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/2 by allen
"""

from logging import DEBUG

import click
import logger

import config
from init_handler import do_init

VERSION = "0.1.1"


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


@cli.command()
@click.option('-d', '--debug', is_flag=True, callback=open_debug,
              expose_value=False, is_eager=True)
@click.option('-n', '--name', prompt=True, help="project name")
@click.option('-v', '--version', default=config.TEMPLATE_VERSION, help="project version")
@click.option('-o', '--owner', default=config.TEMPLATE_OWNER, help="project owner")
@click.option('-e', '--email', default=config.TEMPLATE_EMAIL, help="project email")
def init(name, version, owner, email):
    logger.debug("raw input project name: {0}, version {1}, owner: {2}, email: {3}".format(
        name, version, owner, email
    ))

    do_init(name, version, owner, email)


if __name__ == '__main__':
    cli()
