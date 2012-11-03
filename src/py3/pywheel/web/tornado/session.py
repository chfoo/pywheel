'''HTTP State Management'''
# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
import abc
import contextlib
import time
import uuid


class Session(dict):
    '''A ``dict`` with properties'''

    __slots__ = ()
    ID = '_id'
    LAST_MODIFIED = '_last_mod'
    COOKIE_TIMESTAMP = '_cookie_time'
    PERSISTENT = '_persist'
    UNCHECKED_KEYS = frozenset((LAST_MODIFIED, COOKIE_TIMESTAMP, PERSISTENT))

    def __init__(self, *args, **kwargs):
        self.id = None
        self.last_modified = 0
        self.cookie_timestamp = 0
        self.persistent = False
        dict.__init__(self, *args, **kwargs)

    @property
    def id(self):
        '''The session ID (bytes)'''
        return self[Session.ID]

    @id.setter
    def id(self, id_):
        self[Session.ID] = id_

    @property
    def last_modified(self):
        '''When the session was last modified (Unix timestamp)'''
        return self[Session.LAST_MODIFIED]

    @last_modified.setter
    def last_modified(self, timestamp):
        self[Session.LAST_MODIFIED] = timestamp

    @property
    def cookie_timestamp(self):
        '''When cookie was last send to the client (Unix timestamp)'''
        return self[Session.COOKIE_TIMESTAMP]

    @cookie_timestamp.setter
    def cookie_timestamp(self, timestamp):
        self[Session.COOKIE_TIMESTAMP] = timestamp

    @property
    def persistent(self):
        '''Whether the cookie is persistent in the web browser (boolean)

        ``True``
            The cookie is saved in the browser for at least 30 days.
        ``False``
            The cookie is deleted when the browser is closed.
        '''
        return self[Session.PERSISTENT]

    @persistent.setter
    def persistent(self, b):
        if b != self.get(Session.PERSISTENT):
            self.cookie_timestamp = 0

        self[Session.PERSISTENT] = b

    @property
    def dirty(self):
        if Session.ID in self:
            return True

        for k in self.keys():
            if k not in Session.UNCHECKED_KEYS:
                return True

        return False


class BaseSessionController(object, metaclass=abc.ABCMeta):
    '''Manages sessions or HTTP states'''

    COOKIE_NAME = 'pywheelsid'
    COOKIE_SET_INTERVAL = 1296000  # 15 days
    EXPIRE_TIME = 2678400  # 31 days

    @abc.abstractmethod
    def get_session_dict(self, id_):
        '''Return the session dict given an ID.'''
        pass

    @abc.abstractmethod
    def save_session_dict(self, session_dict):
        '''Save the session dict.

        :type session_dict: :class:`Session`

        .. note::

            As a post-condition, the ID of `session_dict` must be set.
        '''
        pass

    @abc.abstractmethod
    def clean(self):
        '''Delete expired sessions.'''
        pass

    @contextlib.contextmanager
    def __call__(self, request_handler, save=True):
        '''Return a session to be used using the ``with`` statement.

        :type request_handler: :class:`tornado.web.RequestHandler`
        :rtype: :class:`Session`
        '''
        session = self._get_session(request_handler)

        assert session is not None

        yield session

        need_set_cookie = time.time() - session.cookie_timestamp > \
            BaseSessionController.COOKIE_SET_INTERVAL

        if save and session.dirty:
            if need_set_cookie:
                session.cookie_timestamp = int(time.time())

            session.last_modified = int(time.time())
            self.save_session_dict(session)

            if need_set_cookie:
                self._send_cookie(request_handler, session)

    def _get_session(self, request_handler):
        '''Get a stored session or a new session.'''
        session_id = request_handler.get_secure_cookie(
            BaseSessionController.COOKIE_NAME)
        session = self._new_session_dict()

        if session_id:
            stored_session_dict = self.get_session_dict(session_id)

            if stored_session_dict is not None:
                session.update(stored_session_dict)

        return session

    def _new_session_dict(self):
        '''Return a new session.'''
        return Session()

    def _send_cookie(self, request_handler, session):
        '''Send a cookie to the browser.'''
        expires_days = 30 if session.persistent else None

        request_handler.set_secure_cookie(BaseSessionController.COOKIE_NAME,
            session.id, expires_days=expires_days)


class MemorySessionController(BaseSessionController):
    '''Provides a in-memory session controller for testing.'''
    def __init__(self):
        self._table = {}

    def get_session_dict(self, id_):
        return self._table.get(id_)

    def save_session_dict(self, session_dict):
        id_ = uuid.uuid4().bytes
        session_dict.id = id_
        self._table[id_] = session_dict

    def clean(self):
        time_now = time.time()

        for k in list(self._table.keys()):
            session = self._table[k]

            if session.last_modified - time_now > \
            BaseSessionController.EXPIRE_TIME:
                del self._table[k]
