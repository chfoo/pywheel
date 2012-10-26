# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
from pywheel.coroutine import coroutine
import unittest


def my_undec_coroutine():
    while True:
        (yield)


@coroutine
def my_coroutine():
    while True:
        (yield)


class TestCoroutine(unittest.TestCase):
    def test_failure(self):
        '''It should not automatically start the coroutine'''

        c = my_undec_coroutine()

        def f():
            c.send('asdf')

        self.assertRaises(TypeError, f)

    def test_coroutine(self):
        '''It should automatically start the coroutine'''

        c = my_coroutine()
        c.send('asdf')
