"""
The MIT License (MIT)

Copyright (c) 2019 Yuri Andreev Jr.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import sys

from setuptools import setup, find_packages

setup(
    name = 'pyawad',
    version = '0.0.2',
    packages = find_packages(),

    author = 'Yuri Andreev Jr.',
    author_email = 'andreev.jr@gmail.com',
    description = 'Anywayanyday API python wrapper',
    long_description = open('README.md').read(),

    license = 'MIT',
    keywords = 'anywayanyday api aiohttp',
    url='https://github.com/netstuff/pyawad',
    download_url='https://github.com/netstuff/pyawad/archive/master.zip',
    install_requires = [
      'aiohttp',
      'pytest-asyncio-0.10.0',
      'xmlschema',
    ],
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)
