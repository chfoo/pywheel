from pywheel.tornado.session import MemorySessionController
from tornado.httputil import url_concat
import http.client
import tornado.testing
import tornado.web


class SessionHandler(tornado.web.RequestHandler):
    def get(self, action):
        with self.application.session(self) as session:
            if action == 'set':
                session['text'] = self.get_argument('text')

                if self.get_argument('persistent', False):
                    session.persistent = True
                else:
                    session.persistent = False

            self.write(session.get('text', ''))


class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, [
                ('/session/(.*)', SessionHandler),
            ],
            cookie_secret='kitteh')
        self.session = MemorySessionController()


class TestSessionController(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def test_invalid_id(self):
        '''It should return no data with invalid id'''

        self.http_client.fetch(self.get_url('/session/'), self.stop)

        response = self.wait()

        self.assertEqual(response.code, http.client.OK)
        self.assertFalse(response.body)

    def test_save_text(self):
        '''It should save the text'''

        self.http_client.fetch(self.get_url('/session/set?text=kittens'),
            self.stop)

        response = self.wait()

        self.assertEqual(response.code, http.client.OK)
        self.assertEqual(response.body.decode(), 'kittens')

        cookie_value = response.headers['Set-Cookie']

        self.assertNotIn('expires', cookie_value,
            'It should be session cookie')

        self.http_client.fetch(self.get_url('/session/'),
            self.stop, headers={'Cookie': cookie_value})

        response = self.wait()

        self.assertEqual(response.code, http.client.OK)
        self.assertEqual(response.body.decode(), 'kittens')

    def test_persistent(self):
        '''It should save the text and give persistent cookie (30 or 31 days)
        '''

        self.http_client.fetch(self.get_url('/session/set?text=kittens'),
            self.stop)

        response = self.wait()

        self.assertEqual(response.code, http.client.OK)

        cookie_value = response.headers['Set-Cookie']

        self.assertNotIn('expires', cookie_value,
            'It should be session cookie')

        self.http_client.fetch(url_concat(self.get_url('/session/set'),
            {'text': 'kittens', 'persistent': 'yes'}),
            self.stop, headers={'Cookie': cookie_value},)

        response = self.wait()

        self.assertEqual(response.code, http.client.OK)

        cookie_value = response.headers['Set-Cookie']

        self.assertIn('expires', cookie_value,
            'It should be a persistent cookie')
