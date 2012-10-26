'''Basic DBM-style for json-serializable data in sqlite3 database'''
# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
from pywheel.db.sqlite import Connector
import collections
import json


class Database(collections.MutableMapping):
    '''A dict-like object that uses SQLite as the storage'''

    def __init__(self, path):
        self._connector = Connector(path)

        with self._connector() as connection:
            connection.execute('CREATE TABLE IF NOT EXISTS '
                't(k TEXT PRIMARY KEY, v TEXT)'
            )

    def __len__(self):
        with self._connector() as connection:
            cursor = connection.execute('SELECT SUM(1) FROM t')
            row = cursor.fetchone()

            if row and row[0]:
                return int(row[0])
            else:
                return 0

    def keys(self):
        return list(self.__iter__())

    def __iter__(self):
        with self._connector() as connection:
            cursor = connection.execute('SELECT k FROM t')

            for row in cursor:
                yield row[0]

    def __getitem__(self, k):
        with self._connector() as connection:
            cursor = connection.execute('SELECT v FROM t WHERE k = ?', [k])
            row = cursor.fetchone()

            if row:
                return json.loads(row[0])
            else:
                raise IndexError()

    def __contains__(self, k):
        try:
            self[k]
            return True
        except IndexError:
            return False

    def __setitem__(self, k, v):
        with self._connector() as connection:
            connection.execute('INSERT OR REPLACE INTO t (k, v) '
                'VALUES ( ?, ? )', [k, json.dumps(v)])

    def __delitem__(self, k):
        with self._connector() as connection:
            connection.execute('DELETE FROM t WHERE k = ? ', [k])

    def update(self, k, v):
        d = self[k]
        d.update(v)
        self[k] = d
