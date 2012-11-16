'''Python Middleware and Utilities

PyWheel is a collection of Python middleware and utilities. These modules
are focused on web development.
'''
# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
import distutils.version


short_version = '0.1'  # N.N
__version__ = short_version + ''  # N.N[.N]+[{a|b|c|rc}N[.N]+][.postN][.devN]
short_description, long_description = __doc__.split('\n', 1)

distutils.version.StrictVersion(__version__)
