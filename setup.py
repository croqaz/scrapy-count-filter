#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

# https://github.com/kennethreitz/setup.py ✨ 🍰 ✨

NAME = 'scrapy-count-filter'
DESCRIPTION = 'Scrapy Middleware for limiting requests based on a counter.'
KEYWORDS = 'scrapy counter filter'
URL = 'https://github.com/croqaz/scrapy-count-filter'
AUTHOR = 'Cristi Constantin'
EMAIL = 'cristi.constantin@live.com'

REQUIRES_PYTHON = '>=3.6.0'
REQUIRED = ['scrapy>=1.5']

here = os.path.abspath(os.path.dirname(__file__))
about = {}

with open(os.path.join(here, NAME.replace('-', '_'), '__version__.py')) as f:
    exec(f.read(), about)

setup(
    version=about['__version__'],
    name=NAME,
    description=DESCRIPTION,
    keywords=KEYWORDS,
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,
    license='BSD',
    packages=find_packages(),
    platforms=['Any'],
    python_requires=REQUIRES_PYTHON,
    install_requires=REQUIRED,
    classifiers=[
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development',
    ])
