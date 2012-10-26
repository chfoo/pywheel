'''Coroutine helpers'''
# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
import functools


def coroutine(func):
    '''A decorator function that takes care of starting a coroutine
    automatically on call.

    :See: http://www.dabeaz.com/coroutines/
    '''

    @functools.wraps(func)
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)

        next(cr)

        return cr

    return start
