# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
from pywheel.backoff import ExpBackoff, Trier
import unittest


class TestExpBackoff(unittest.TestCase):
    def test_inc(self):
        '''It should increment to cap'''

        backoff = ExpBackoff(init=1.0, rate=2.0, cap=10, deviation=0.3)

        self.assertEqual(1.0, backoff.value)
        self.assertEqual(2.0, backoff.inc())
        self.assertEqual(4.0, backoff.inc())
        self.assertEqual(8.0, backoff.inc())
        self.assertAlmostEqual(10.0, backoff.inc(), delta=10 * 0.3)
        self.assertAlmostEqual(10.0, backoff.inc(), delta=10 * 0.3)

    def test_reset(self):
        '''It should reset value to initial value'''

        backoff = ExpBackoff(init=1.0, rate=2.0, cap=10, deviation=0.3)

        backoff.inc()
        backoff.reset()

        self.assertEqual(1.0, backoff.value)


class TestTrier(unittest.TestCase):
    def test_start_stop(self):
        '''It should start and stop within 0.1 second.'''

        def f():
            return False

        trier = Trier(f)
        trier.stop()
        trier.join(timeout=0.1)
        self.assertFalse(trier.is_alive())
