# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/25 by allen
"""

import os
import codecs
from setuptools import setup, find_packages

from tadpole.config import VERSION
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    long_description = f.read()


NAME = "tadpole"
__version__ = VERSION
__author__ = "allen"
__license__ = "MIT"
__copyright__ = "2017 - allen"


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


def required_packages():
    with codecs.open("requirements.txt", "r") as pfp:
        return pfp.readlines()


extra_files = package_files('tadpole/template/')
depend_packages = list(required_packages())

setup(
    name=NAME,
    version=__version__,
    license=__license__,
    author=__author__,
    author_email='echoyuanliang@gmail.com',
    description="flask starter",
    long_description=long_description,
    url='https://github.com/echoyuanliang/tadpole',
    download_url='https://github.com/echoyuanliang/tadpole.git',
    install_requires=depend_packages,
    packages=find_packages(),
    package_data={'': extra_files},
    keywords=['flask', 'restful', 'orm', 'sqlalchemy', 'auth', 'permission'],
    platforms='any',
    classifiers=[
        'Operating System :: POSIX',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    entry_points="""
    [console_scripts]
    tadpole=tadpole.run:cli
    """
)
