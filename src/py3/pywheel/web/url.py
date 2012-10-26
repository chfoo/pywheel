'''URL and URI utilities for normalization and canonicalization

All operations are done on `str` objects. Parsers expect strings that can
be encoded to ASCII. The caller is responsible for
decoding non-ASCII (and improper) URLs.
'''
# This file is part of PyWheel.
# Copyright © 2011-2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
import cgi
import collections
import copy
import io
import urllib.parse

DEFAULT_PORTS = {
    'ftp': 21,
    'gopher': 70,
    'hdl': 2641,
    'http': 80,
    'https': 443,
    'imap': 143,
    'nntp': 119,
    'propsero': 191,
    'rsync': 873,
    'rtsp': 554,
    'sftp': 115,
    'sip': 5060,
    'svn': 3690,
    'telnet': 23,
}


class URLQuery(collections.defaultdict):
    '''URL query one-to-many mapping.

    The keys are ``str``s. The values are a ``list`` of ``str``s.
    '''

    def __init__(self, query_map=None, url_str=None):
        '''Initialize a map

        :param query_map: A mapping of query values (``str``).
            Both one-to-one and one-to-many mappings are accepted and
            one-to-one mappings are automatically converted to one-to-many
            mappings.
        :param url_str: A percent-encoded URL query.
        :type url_str: ``str``
        '''

        collections.defaultdict.__init__(self, list)

        if url_str:
            query_map = urllib.parse.parse_qs(url_str, True)

        if query_map:
            for key, value_list in query_map.items():
                if isinstance(value_list, str):
                    value_list = [value_list]

                value_list.sort()
                self[key] = value_list

    def getfirst(self, key, default=None):
        '''Get the first value for a key

        :rtype: `str`
        '''

        return self.get(key, (default,))[0]

    def __str__(self):
        '''Return the percent-encoded url query form

        :rtype: `str`
        '''

        buf = io.StringIO()
        needs_trim = False

        for key in sorted(self.keys()):
            value_list = self[key]

            if not value_list:
                continue

            needs_trim = True

            for value in value_list:
                buf.write(urllib.parse.quote(key))

                if value:
                    buf.write('=')
                    buf.write(urllib.parse.quote(value))

                buf.write('&')

        if needs_trim:
            buf.seek(buf.tell() - 1)
            buf.truncate()

        return buf.getvalue()

    def one_to_one_map(self):
        '''Return a plain `dict` with one-to-one mapping.

        In other words, return a ``dict`` that has a key and a value.
        If there is a key with more than one value, the value is arbitrarily
        chosen.
        '''

        new_dict = {}
        for key, value_list in self.items():
            new_dict[key] = value_list[0]

        return new_dict


class URL(object):
    '''A fancy URL parser and builder

    It helps with normalization and canonicalization of URLs.
    '''

    def __init__(self, encoded_string=None, scheme=None, username=None,
    password=None, hostname=None, port=None, path=None, params=None,
    query_map=None, fragment=None, keep_trailing_slash=True):
        '''Initialize the URL object

        :parameters:
            encoded_str : `str`
                A valid encoded URL.
            scheme: `str`
                The scheme portion. For example, http and ftp.
            username: `str`
                The username portion.
            password: `str`
                The password portion.
            hostname: `str`
                The hostname portion.
            port: `int`
                The port number.
            path: `str`
                The path portion without the parameter portion.
            params: `str`
                The parameters portion.
            query_map: `dict`
                A key and value list map of query values.
            fragment: `str`
                The fragment portion
            keep_trailing_slash: `bool`
                If `True`, the trailing slash of the path is not stripped.
                Technically, a trailing slash indicates a directory and a
                non-trailing slash indicate a file. However, this semantic
                is not intuitive to regular web users. On a search engine
                optimization perspective, the trailing slash usually matters.
        '''

        self._scheme = scheme
        self._username = username
        self._password = password
        self._hostname = hostname
        self._port = port
        self._path = path
        self._params = params
        self._query = URLQuery(query_map=query_map)
        self._fragment = fragment

        if encoded_string is not None:
            self.parse(encoded_string)

    @property
    def scheme(self):
        return self._scheme

    @scheme.setter
    def scheme(self, s):
        self._scheme = s

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, s):
        self._username = s

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, s):
        self._password = s

    @property
    def hostname(self):
        return self._hostname

    @hostname.setter
    def hostname(self, s):
        self._hostname = s

    @property
    def port(self):
        if self._port:
            return self._port
        else:
            return DEFAULT_PORTS.get(self.scheme)

    @port.setter
    def port(self, n):
        self._port = int(n)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, s):
        if not s.startswith('/'):
            s = '/%s' % s

        self._path = collapse_path(s)

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, s):
        self._params = urllib.parse.unquote(s)

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, o):
        if isinstance(o, str):
            self._query = URLQuery(encoded_string=o)
        else:
            self._query = URLQuery(query_map=o)

    @property
    def fragment(self):
        return self._fragment

    @fragment.setter
    def fragment(self, s):
        self._fragment = s

    def __str__(self):
        s = io.StringIO()

        if self._scheme:
            s.write(self.scheme)
            s.write(':')

        if self._hostname:
            s.write('//')

        if self._username:
            s.write(urllib.parse.quote_plus(self._username.encode()))

        if self._password:
            s.write(':')
            s.write(urllib.parse.quote_plus(self._password.encode()))

        if self._username:
            s.write('@')

        if self._hostname:
            s.write(to_punycode_hostname(self._hostname))

        if self._port and DEFAULT_PORTS.get(self._scheme) != self._port:
            s.write(':')
            s.write(str(self._port))

        if self._path:
            s.write(urllib.parse.quote(self._path))

        if self._params:
            s.write(';')
            s.write(self._params)

        if self._query:
            s.write('?')
            s.write(str(self._query))

        if self._fragment:
            s.write('#')
            s.write(urllib.parse.quote(self._fragment.encode()))

        s.seek(0)
        return s.read()

    def __repr__(self):
        return '<URL (%s) at 0x%x>' % (self.__str__(), id(self))

    def to_string(self):
        return self.__str__()

    def parse(self, s):
        assert isinstance(s, str)

        p = urllib.parse.urlparse(s)

        self._scheme = p.scheme
        self._username = urllib.parse.unquote(p.username) if p.username \
            else None
        self._password = urllib.parse.unquote(p.password) if p.password \
            else None
        self._hostname = from_punycode_hostname(p.hostname) if p.hostname \
            else None
        self._port = int(p.port) if p.port else None
        self._path = collapse_path(p.path) or '/'
        self._params = p.params
        self._query = URLQuery(url_str=p.query)
        self._fragment = urllib.parse.unquote(p.fragment) if p.fragment \
            else None

    def get_query_first(self):
        d = {}

        for k in self.query:
            d[k] = self.query.getfirst(k)

        return d

    def copy(self):
        return copy.copy(self)


class FieldStorage(cgi.FieldStorage):
    def getfirst(self, *args, **kargs):
        v = cgi.FieldStorage.getfirst(self, *args, **kargs)

        if isinstance(v, str):
            return v.decode()
        else:
            return v

    def getlist(self, *args, **kargs):
        l = cgi.FieldStorage.getlist(self, *args, **kargs)

        new_list = l

        for i in range(len(l)):
            v = l[i]

            if isinstance(v, str):
                new_list[i] = v.decode()

        return new_list


def is_allowable_hostname(s):
    return all([c in ('-', '.') or 48 <= ord(c) <= 57 or 97 <= ord(c) <= 127 \
        for c in s])


def normalize(s):
    return str(URL(s))


def collapse_path(s, keep_trailing_slash=True):
    l = []

    for part in s.replace('//', '/').split('/'):
        part = urllib.parse.unquote(part)
        if part == '..':
            if len(l):
                del l[-1]

                if s.endswith('..'):
                    l.append('')

        elif (part or keep_trailing_slash) and part != '.':
            l.append(part)

    return '/'.join(l)


def from_punycode_hostname(s):
    if not is_allowable_hostname(s):
        return s
    else:
        s = str(s)

    h = s.split('.')
    if len(h) > 1 and h[-2].startswith('x--'):
        h[-2] = bytes(h[-2].replace('x--', '', 1), 'utf8').decode('punycode')
    return '.'.join(h)


def to_punycode_hostname(s):
    if is_allowable_hostname(s):
        return s
    else:
        h = s.split('.')
        h[-2] = 'x--' + str(h[-2].encode('punycode'), 'utf8')
        return '.'.join(h)
