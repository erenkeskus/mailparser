#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os import path
import io

here = path.abspath(path.dirname(__file__))

NAME = 'mailparser'
with io.open(path.join(here, 'version.py'), 'rt', encoding='UTF-8') as f:
    exec(f.read())

setup(
    name=NAME,
    version=__version__,
    description=('Parse mail attachments and inserts data into the database. '
                 + 'You need to implement a parser class for your file type.'),
    author=__author__,
    author_email=__email__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='python parse mail import file',

    packages=find_packages(exclude=['tests', ]),
    install_requires=['pandas'],
    entry_points={
       'console_scripts': [
           'import-attachment=mailparser.run:execute',
       ],
    }
)
