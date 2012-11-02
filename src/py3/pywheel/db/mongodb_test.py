# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
from pymongo.connection import Connection
from pywheel.db.mongodb import SessionController, Reconnector
from pywheel.web.tornado.session import Session
import time
import unittest


class TestSessionController(unittest.TestCase):
    def setUp(self):
        conn = Connection()
        db = conn.test
        self.coll = db.test

    def tearDown(self):
        self.coll.drop()

    def test_save_and_get(self):
        '''It should save and return the data'''

        s = SessionController(self.coll)
        session_dict = Session()
        session_dict['hello'] = 'kitten'

        s.save_session_dict(session_dict)

        test_dict = s.get_session_dict(session_dict.id)

        self.assertTrue(test_dict)
        self.assertEqual('kitten', test_dict['hello'])


class TestReconnector(unittest.TestCase):
    def test_fail(self):
        '''It should not crash if database is not online'''

        reconnector = Reconnector(host='nonexistant.invalid')
        time.sleep(0.01)
        reconnector.stop()
        reconnector.join()
