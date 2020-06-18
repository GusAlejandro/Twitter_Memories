import unittest
from configuration.app_config import TestConfig, TestGCPConfig
from twittermemories import create_app
from twittermemories.models import db
from celeryworker.tasks import process_tweets


class TestCelery(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app.testing = True
        self.app = self.app.test_client()
        self.app_context.push()
        db.create_all()        
        print("asdf")

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add(self):
        process_tweets.apply(args=('tweet', TestGCPConfig, TestConfig))
    

if __name__ == '__main__':
    unittest.main()
