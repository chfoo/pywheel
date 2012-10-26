# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
from pywheel.web.bootstrap import Bootstrap
import tempfile
import textwrap
import unittest


class TestBootstrap(unittest.TestCase):
    def test_plain(self):
        '''It should be ok without anything'''

        Bootstrap(argv=[])

    def test_load_config(self):
        '''It should load a config filename passed as argument'''

        config_file = tempfile.NamedTemporaryFile()
        config_file.write(textwrap.dedent('''[my_section]
            my_config: abc
        ''').encode())
        config_file.flush()

        bootstrap = Bootstrap(argv=['--config', config_file.name])

        self.assertEqual(bootstrap.config_parser['my_section']['my_config'],
            'abc')
