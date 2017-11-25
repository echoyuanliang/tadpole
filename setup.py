# !/usr/bin/python
# coding: utf-8

"""
    create at 2017/11/25 by allen
"""

import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    long_description = f.read()


NAME = "tadpole"
__version__ = '1.0.1'
__author__ = "allen"
__license__ = "MIT"
__copyright__ = "2017 - allen"


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('tadpole/template/')

setup(
    name=NAME,
    version=__version__,
    license=__license__,
    author=__author__,
    author_email='echoyuanliang@gmail.com',
    description=__doc__,
    long_description=long_description,
    url='https://github.com/echoyuanliang/tadpole',
    download_url='https://github.com/echoyuanliang/tadpole.git',
    install_requires=[
        "click==6.7",
        "termcolor==1.1.0"
    ],
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
