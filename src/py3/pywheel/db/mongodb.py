'''Middleware and Utilities for MongoDB'''
# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
from bson.objectid import ObjectId
from pymongo.connection import Connection
from pymongo.errors import ConnectionFailure
from pywheel.backoff import ExpBackoff, Trier
from pywheel._gettexthelper import _
from pywheel.web.tornado.session import BaseSessionController
import datetime
import logging
import time

_logger = logging.getLogger(__name__)


class Reconnector(Trier):
    def __init__(self, *args, **kwargs):
        '''Repeatedly attempt to establish a MongoDB connection.

        Arguments are passed to :class:`pymongo.connection.Connection`.
        '''

        Trier.__init__(self, self._try_connect, backoff=ExpBackoff(cap=600))
        self._conn_args = args, kwargs
        self._conn = None

    def _try_connect(self):
        try:
            self._conn = Connection(*self._conn_args[0], **self._conn_args[1])
        except ConnectionFailure:
            self._conn = None

            _logger.exception(_('Failed to connect to database server'))

            return False
        else:
            return True

    @property
    def conn(self):
        '''Return the connection.

        :rtype: :class:`pymongo.connection.Connection`.
        '''
        return self._conn


class SessionController(BaseSessionController):
    DATA = 'dat'
    LAST_MODIFIED = 'last_mod'

    def __init__(self, collection):
        '''Session controller using MongoDB

        :type collection: :class:`pymongo.collection.Collection`
        '''
        self._collection = collection

    def get_session_dict(self, id_):
        doc = self._collection.find_one({'_id': ObjectId(id_)})

        if doc:
            return doc[self.DATA]

    def save_session_dict(self, session_dict):
        if not session_dict.id:
            session_dict.id = ObjectId().binary

        self._collection.save({
            '_id': ObjectId(session_dict.id),
            self.LAST_MODIFIED: datetime.datetime.utcfromtimestamp(
                session_dict.last_modified),
            self.DATA: session_dict
        })

    def clean(self):
        expire_date = datetime.datetime.fromtimestamp(
            time.time() - BaseSessionController.EXPIRE_TIME)

        self._collection.remove({self.LAST_MODIFIED: {'$lt': expire_date}})
