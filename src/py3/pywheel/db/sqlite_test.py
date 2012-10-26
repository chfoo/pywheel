# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
from pywheel.db.sqlite import Connector
import os.path
import tempfile
import time
import unittest


class TestSqliteConnector(unittest.TestCase):
    def test_simple(self):
        '''It should not crash.'''

        tempdir = tempfile.TemporaryDirectory()
        connector = Connector(os.path.join(tempdir.name, 'kittens.db'))

        with connector() as connection:
            connection.execute('CREATE TABLE kittens '
                '(id INTEGER PRIMARY KEY, name TEXT)')

        with connector() as connection:
            connection.execute('INSERT INTO kittens (name) VALUES ("kitteh")')

        with connector() as connection:
            cur = connection.execute('SELECT name FROM kittens')
            row = cur.fetchone()

            self.assertEqual(row[0], 'kitteh')
