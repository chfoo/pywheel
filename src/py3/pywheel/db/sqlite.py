'''SQLite helpers'''
# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
import contextlib
import sqlite3


class Connector(object):
    '''A wrapped SQLite connection.

    By default, it sets the connection up with fastness and foreign keys.

    Example::

        connector = Connector("/tmp/kittens.db")

        with connector() as connection:
            connection.execute("SOME STATEMENTS")

    '''

    def __init__(self, path, **sqlite_kwargs):
        '''Create a new connection using given path.'''

        kwargs = dict(isolation_level='DEFERRED',
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        kwargs.update(sqlite_kwargs)

        self._kwargs = kwargs
        self._path = path

    @contextlib.contextmanager
    def __call__(self):
        con = sqlite3.connect(self._path, **self._kwargs)

        con.row_factory = sqlite3.Row
        con.execute('PRAGMA synchronous=NORMAL')
        con.execute('PRAGMA journal_mode=WAL')
        con.execute('PRAGMA foreign_keys=ON')

        with con:
            yield con

    @property
    def database_size(self):
        '''The size of the database.

        :rtype: ``int``
        '''

        with self() as con:
            cur = con.execute('PRAGMA page_count')
            page_count = cur.fetchone()[0]
            cur = con.execute('PRAGMA page_size')
            page_size = cur.fetchone()[0]

        return page_count * page_size
