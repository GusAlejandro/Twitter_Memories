import unittest
from configuration.app_config import TestConfig
from flask import Flask


class TestViews(unittest.TestCase):

    def setUp(self):
        app = Flask(__name__)
        app.config.from_object(TestConfig)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
