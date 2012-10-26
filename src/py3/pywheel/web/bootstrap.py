'''Helpers for starting applications'''
# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
from pywheel._gettexthelper import _
import argparse
import configparser
import sys


class Bootstrap(object):
    def __init__(self, arg_parser=None, config_parser=None, argv=None):
        '''Helps to gather settings needed for applications.'''
        super()

        self._sys_argv = argv if argv is not None else sys.argv[1:]
        self._arg_parser = arg_parser or argparse.ArgumentParser(
            description=_('Web application with no defined description'))
        self._config_parser = config_parser or configparser.ConfigParser()

        self._parse_args()
        self._load_config()

    @property
    def arg_parser(self):
        '''Return the :class:`argparse.ArgumentParser`.'''
        return self._arg_parser

    @property
    def args(self):
        '''Return the arguments passed to the program.'''
        return self._args

    @property
    def config_parser(self):
        '''Return the :class:`configparser.ConfigParser`.'''
        return self._config_parser

    def _parse_args(self):
        self._arg_parser.add_argument('--config', '-c', action='append',
            help=_('Path of configuration file'))

        self._args = self._arg_parser.parse_args(self._sys_argv)

    def _load_config(self):
        if self._args.config:
            self._config_parser.read(self._args.config)
