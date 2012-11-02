'''Rate limiting using backoff algorithms'''
# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
import random
import threading


class ExpBackoff(object):
    def __init__(self, init=1.0, rate=2.0, cap=3600.0, deviation=0.3):
        '''Exponential backoff counter

        :param init: The initial value
        :param rate: The rate at which the value grows
        :param cap: The maximum limit
        :param deviation: The factor in terms of `cap` in which the value will
            range. In other words, once the cap is reached, a value will be
            returned in the random range of [cap ± cap × deviation]
        '''

        self._value = self._init = init
        self._rate = rate
        self._cap = cap
        self._std_dev = deviation

    def reset(self):
        '''Reset the counter to its initial value.'''
        self._value = self._init

    def inc(self):
        '''Increment the counter to the next value and return it.'''
        self._value *= self._rate

        if self._value > self._cap:
            deviation = self._cap * self._std_dev
            self._value = random.uniform(self._cap - deviation,
                self._cap + deviation)

        return self._value

    @property
    def value(self):
        '''Return the current value.'''
        return self._value


class Trier(threading.Thread):
    def __init__(self, fn, args=(), kwargs={}, autostart=True, backoff=None):
        '''Repeatedly attempt an operation.

        :param fn: The callable object.
        :param args: Positional arguments to be passed to the callable.
        :param kwargs: Keyword arguments to be passed to the callable.
        :param autostart: If `True`, the thread is started automatically.
        :type autostart: `bool`
        :param backoff: An alternative backoff counter object.

        The callable should return `bool`. If the callable returns `True`,
        then the operation is a success. If the callable returns `False`,
        the operation failed and will be tried again.
        '''
        threading.Thread.__init__(self)
        self.name = Trier.__class__.__name__
        self.daemon = True
        self._backoff = backoff or ExpBackoff()
        self._fn = fn
        self._fn_args = args
        self._fn_kwargs = kwargs
        self._run_event = threading.Event()

        if autostart:
            self.start()

    def start(self):
        self._run_event.clear()
        threading.Thread.start(self)

    def run(self):
        while not self._run_event.isSet():
            result = self._fn(*self._fn_args, **self._fn_kwargs)

            if result:
                self._backoff.reset()
                self._run_event.set()
            else:
                self._run_event.wait(self._backoff.inc())

    def stop(self):
        '''Stop attempt.'''
        self._run_event.set()
