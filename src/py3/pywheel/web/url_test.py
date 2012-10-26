'''URL N11n testing'''
# This file is part of PyWheel.
# Copyright © 2012 Christopher Foo <chris.foo@gmail.com>.
# Licensed under GNU GPLv3. See COPYING.txt for details.
from pywheel.web.url import (URL, collapse_path, to_punycode_hostname,
    from_punycode_hostname, is_allowable_hostname)
import unittest

__docformat__ = 'restructuredtext en'


class TestURL(unittest.TestCase):
    @unittest.skip('url not parsed correctly by python lib')
    def test_parse_mailto(self):
        s = 'mailto:user@example.com'
        url = URL(s)
        self.assertEqual(url.scheme, 'mailto')
        self.assertEqual(url.username, 'user')
        self.assertEqual(url.hostname, 'example.com')
        self.assertEqual(str(url), s)

    def test_parse_http(self):
        '''It should accept a URL and unescape each part. It should
        support queries with multiple keys with the same name.'''

        s = 'http://user:password@example.com:8080/' \
            '~justin/kittens%C2%A4;a' \
            '?q=b&q=a&e&b=%C3%A4%C3%A5%C3%A9%C3%AB%C3%BE%C3%BC%C3%BA%C3%AD' \
            '%C3%B3%C3%B6%C3%A1%C3%9F%C3%B0fgh%C3%AF%C5%93%C3%B8%C3%A6%C5' \
            '%93%C2%A9%C2%AEb%C3%B1&q=c&d=f#s'

        url = URL(s)
        self.assertEqual(url.scheme, 'http')
        self.assertEqual(url.username, 'user')
        self.assertEqual(url.password, 'password')
        self.assertEqual(url.hostname, 'example.com')
        self.assertEqual(url.port, 8080)
        self.assertEqual(url.path, '/~justin/kittens¤')
        self.assertEqual(url.params, 'a')
        self.assertEqual(url.fragment, 's')
        self.assertEqual(url.query.get('q'), ['a', 'b', 'c'])  # sorted
        self.assertEqual(url.query.getfirst('q'), 'a')
        self.assertEqual(url.query.get('d'), ['f'])
        self.assertEqual(url.query.getfirst('d'), 'f')
        self.assertEqual(url.query.getfirst('b'), 'äåéëþüúíóöáßðfghïœøæœ©®bñ')

    def test_parse_hostname_unicode(self):
        '''It should not change unencoded internationalized domains'''

        url = URL('//www.ff¤ë.com')
        self.assertEqual(url.hostname, 'www.ff¤ë.com')

    def test_parse_hostname_punycode(self):
        '''It should decode internationalized domains'''

        url = URL('//www.x--ff-fda8z.com')
        self.assertEqual(url.hostname, 'www.ff¤ë.com')

    def test_collapse_path(self):
        '''It should normalize paths

        1. Leading slashes are *not* removed.
        2. Double slashes are collapsed into one.
        3. Relative paths are simplified into the absolute paths
        4. Trailing slashes are *not* removed
        '''

        s = '/a/b/c/../'
        self.assertEqual(collapse_path(s), '/a/b/')

        s = 'a/b/./c'
        self.assertEqual(collapse_path(s), 'a/b/c')

        s = '/a/b/c/..'
        self.assertEqual(collapse_path(s), '/a/b/')

        s = 'a/../b/c'
        self.assertEqual(collapse_path(s), 'b/c')

        s = '/a//b/'
        self.assertEqual(collapse_path(s), '/a/b/')

    def test_default_port_removal(self):
        '''It should accept a URL with the default port for that protocol and
        return the URL without the default port'''

        s = 'http://example.com:80'
        url = URL(s)
        self.assertEqual(str(url), 'http://example.com/')

    def test_to_punycode_hostname(self):
        '''It should correctly encode the international domain'''

        s = 'aa.bb.cc.ačbǔcŏdīe¤f¤.com'
        self.assertEqual(to_punycode_hostname(s),
            'aa.bb.cc.x--abcdef-mhab25gxirn86c.com')
        self.assertEqual(to_punycode_hostname('example.com'),
            'example.com')

    def test_from_punycode_hostname(self):
        '''It should correctly decode the punycode domain'''

        s = 'aa.bb.cc.x--abcdef-mhab25gxirn86c.com'
        self.assertEqual(from_punycode_hostname(s),
            'aa.bb.cc.ačbǔcŏdīe¤f¤.com')
        self.assertEqual(from_punycode_hostname('example.com'),
            'example.com')

    def test_is_allowable_hostname(self):
        '''It should return `True` if the domain has acceptable characters'''

        self.assertTrue(is_allowable_hostname('www.example.com'))
        self.assertFalse(is_allowable_hostname('www.bbéë.com'))

    def test_norm_unicode_http(self):
        '''It should normalize the URL with a international domain'''

        s = 'http://sss.crrffœ³³³éåð.com/ßß³ /dd?df=4ëfð'
        url = URL(s)
        self.assertEqual(str(url), 'http://sss.x--crrff-5iaaa46bib4e48d.com'
            '/%C3%9F%C3%9F%C2%B3%20/dd?df=4%C3%ABf%C3%B0')

    def test_norm_http_query_order(self):
        '''It should sort queries by keys and then values'''

        s = 'http://a.c/p?q=b&q=c&q=a'
        url = URL(s)
        self.assertEqual(str(url), 'http://a.c/p?q=a&q=b&q=c')

    def test_norm_http_ending_slash_and_empty_query(self):
        '''It should *not* remove trailing slash but remove empty queries'''

        self.assertEqual(str(URL('http://ex.com')), 'http://ex.com/')
        self.assertEqual(str(URL('http://ex.com/')), 'http://ex.com/')

        self.assertEqual(str(URL('http://ex.com?d')), 'http://ex.com/?d')
        self.assertEqual(str(URL('http://ex.com/?d')), 'http://ex.com/?d')

        self.assertEqual(str(URL('http://ex.com/a')), 'http://ex.com/a')
        self.assertEqual(str(URL('http://ex.com/a/')), 'http://ex.com/a/')

        self.assertEqual(str(URL('http://ex.com/a/a/?d')),
            'http://ex.com/a/a/?d')

    def test_params_mangling(self):
        '''It should not mangle params'''

        u = URL('http://ex.com/dragon;s?d=r')
        self.assertEqual(u.params, 's')

        u = URL('http://ex.com/dragon;s/?d=r')
        self.assertFalse(u.params)
        self.assertEqual(u.path, '/dragon;s/')
