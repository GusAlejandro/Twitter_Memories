import unittest
from configuration.app_config import TestConfig
from twittermemories import create_app
from google.cloud import storage
from twittermemories.models import db, User, Tweet
import io
import os
import json 

# TEST_DB = 'testing.db'

class TestViews(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app.testing = True
        self.app = self.app.test_client()
        self.app_context.push()
        db.create_all()
        # seed data by uploading test file to GCP    
        storage_client = storage.Client.from_service_account_json(self.app.application.config['CLOUD_STORAGE'].GCP_JSON)
        bucket = storage_client.bucket(self.app.application.config['CLOUD_STORAGE'].GCP_STORAGE_BUCKET)
        blob = bucket.blob('testTwitterArchive.json')
        blob.upload_from_filename(self.app.application.config['TEST_FILE'])
        # seed user into db with id = testTwitterArchive 
        seeded_user = User(raw_password='123', username='TestUser1')
        seeded_user.user_id = 'testTwitterArchive'
        db.session.add(seeded_user)
        # seed tweets into db
        db.session.add(Tweet(tweet_id='TestTweet1', month="Dec", day=31, user=seeded_user))
        db.session.add(Tweet(tweet_id='TestTweet2', month="Jan", day=1, user=seeded_user))
        db.session.add(Tweet(tweet_id='TestTweet3', month="Dec", day=31, user=seeded_user))   
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        os.remove(self.app.application.config['DB_PATH'])

    def test_file_status_defaults_correctly_for_new_user(self):
        response = self.app.post('/register', headers={"Content-Type": "application/json"}, data=json.dumps({"username": "bob", "password": "123pass"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['file_status'], 0)

    def test_login_endpoint(self):
        self.app.post('/register', headers={"Content-Type": "application/json"}, data=json.dumps({"username": "bob", "password": "123pass"}))
        response = self.app.post('/login', headers={"Content-Type": "application/json"}, data=json.dumps({"username": "bob", "password": "123pass"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual('access_token' in response.get_json() and 'refresh_token' in response.get_json(), True)


    def test_get_feed(self):
        response = self.app.post('/login', headers={"Content-Type": "application/json"}, data=json.dumps({"username":"TestUser1", "password":"123"}))
        access_token = response.get_json().get('access_token')
        feed_response = self.app.get('/feed', data=json.dumps({"month": "Dec", "date": 31}), headers={'Authorization': 'Bearer ' + access_token, "Content-Type": "application/json"})
        self.assertEqual(feed_response.status_code, 200)
        self.assertEqual(['TestTweet1','TestTweet3'], feed_response.json['tweets'])

    def test_get_feed_no_params(self):
        response = self.app.post('/login', headers={"Content-Type": "application/json"}, data=json.dumps({"username":"TestUser1", "password":"123"}))
        access_token = response.get_json().get('access_token')
        feed_response = self.app.get('/feed', headers={'Authorization': 'Bearer ' + access_token, "Content-Type": "application/json"})
        self.assertEqual(feed_response.status_code, 400)

    @unittest.skip
    def test_archvie_uplaod(self):
        self.app.post('/register', data={'username': 'bob', 'password': '123pass'})
        response = self.app.post('/login', data={'username': 'bob', 'password': '123pass'})
        access_token = response.get_json()['access_token']
        upload_response = self.app.post('/upload', data= dict(file=(io.BytesIO(b"this is a test"), 'test_tweet_archive.js')), headers={'Authorization': 'Bearer ' + access_token})
        self.assertEqual('status' in upload_response.get_json(), True)


if __name__ == '__main__':
    unittest.main()
