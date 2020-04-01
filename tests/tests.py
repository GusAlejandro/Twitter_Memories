import unittest
from configuration.app_config import TestConfig
from twittermemories import create_app
from twittermemories.models import db
import io

# TEST_DB = 'testing.db'

class TestViews(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app.testing = True
        self.app = self.app.test_client()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_file_status_defaults_correctly_for_new_user(self):
        response = self.app.post('/register', data={'username': 'bob', 'password': '123pass'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['file_status'], 0)

    def test_login_endpoint(self):
        self.app.post('/register', data={'username': 'bob', 'password': '123pass'})
        response = self.app.post('/login', data={'username': 'bob', 'password': '123pass'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('access_token' in response.get_json() and 'refresh_token' in response.get_json(), True)

    def test_archvie_uplaod(self):
        self.app.post('/register', data={'username': 'bob', 'password': '123pass'})
        response = self.app.post('/login', data={'username': 'bob', 'password': '123pass'})
        access_token = response.get_json()['access_token']
        upload_response = self.app.post('/upload', data= dict(file=(io.BytesIO(b"this is a test"), 'testtweets.js')), headers={'Authorization': 'Bearer ' + access_token})
        self.assertEqual('status' in upload_response.get_json(), True)


if __name__ == '__main__':
    unittest.main()
