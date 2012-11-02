# This file is part of PyWheel.
# Copyright © 2011-2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
import os
import pywheel.db.sqlitejsondbm
import tempfile
import unittest

__docformat__ = 'restructuredtext en'


class TestDB(unittest.TestCase):
    def test_simple(self):
        tempdir = tempfile.TemporaryDirectory()
        db = pywheel.db.sqlitejsondbm.Database(os.path.join(tempdir.name,
            'kittens.db'))

        self.assertEqual(0, len(db.keys()))
        self.assertRaises(IndexError, lambda: db['non_existant'])

        d1 = {'some_value': 123}
        db['my_key'] = d1

        self.assertEqual(db['my_key'], d1)

        self.assertEqual(1, len(db.keys()))

        del db['my_key']

        self.assertEqual(0, len(db.keys()))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
