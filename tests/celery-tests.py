import unittest
import os
from configuration.app_config import TestConfig
from twittermemories import create_app
from twittermemories.models import db, User, Tweet
from celeryworker.tasks import process_tweets
from google.cloud import storage 

class TestCelery(unittest.TestCase):
    
    def setUp(self):
        # create application context just to create the db 
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
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        os.remove(self.app.application.config['DB_PATH'])

    def test_archive_processing(self):
        process_tweets.apply(args=('testTwitterArchive', TestConfig))
        all_tweets_query = Tweet.query.all()
        tweetID_list = list(map(lambda tweet: tweet.tweet_id, all_tweets_query))
        self.assertEqual('1229315630374912002' not in tweetID_list, True)
        self.assertEqual('893997805932388352' in tweetID_list, True)

if __name__ == '__main__':
    unittest.main()
