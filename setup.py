#!/usr/bin/env python3

import os
import sys
from distutils.core import setup

src_dir = os.path.abspath(os.path.join('src', 'py3'))
sys.path.insert(0, src_dir)

import pywheel

setup(name='PyWheel',
    version=pywheel.__version__,
    description=pywheel.short_description,
    long_description=pywheel.long_description,
    author='Christopher Foo',
    author_email='chris.foo@gmail.com',
    url='https://launchpad.net/pywheel',
    packages=['pywheel', 
        'pywheel.db', 
        'pywheel.web', 
        'pywheel.web.tornado.',
    ],
    package_dir={'': 'src/py3'},
    package_data={
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.2',
    ],
    requires=[],
)
