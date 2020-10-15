from flask_sqlalchemy import SQLAlchemy
from twittermemories import bcrypt, ma
from configuration.app_config import DatabaseConfig
import datetime
import jwt
import uuid

db = SQLAlchemy()

class Tweet(db.Model):
    __tablename__ = 'Tweet'
    unique_tweet_id = db.Column(db.String, primary_key=True, unique=True)
    tweet_id = db.Column(db.String)
    user_id = db.Column(db.String, db.ForeignKey('User.user_id'), index=True)
    month = db.Column(db.String, index=True)
    day = db.Column(db.Integer)

    def __repr__(self):
        return self.user_id + ' tweed id: ' + self.tweet_id + ' month ' + self.month + ' day ' + str(self.day)

    def __init__(self, **kwargs):
        super(Tweet, self).__init__(**kwargs)
        self.unique_tweet_id = str(uuid.uuid4())


class TweetSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Tweet

    unique_tweet_id = ma.auto_field()
    tweet_id = ma.auto_field()
    month = ma.auto_field()
    day = ma.auto_field()

class User(db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.String, primary_key=True, unique=True)
    username = db.Column(db.String, unique=True, nullable=False)
    hashedPassword = db.Column(db.String)
    file_status = db.Column(db.Integer, default=0)
    tweets = db.relationship('Tweet', backref='user', lazy='dynamic')

    def __init__(self, raw_password, **kwargs):
        super(User, self).__init__(**kwargs)
        self.hashedPassword = User.hash_password(raw_password)
        self.user_id = str(uuid.uuid4())

    def __repr__(self):
        return self.username + ' with id: ' + str(self.user_id)

    @staticmethod
    def hash_password(raw_password):
        return bcrypt.generate_password_hash(raw_password).decode('utf-8')

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.hashedPassword, raw_password)

    @staticmethod
    def encode_auth_token(user_id, token_type):
        if token_type == 'access':
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=10),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id,
                'token_type': 'access'
            }
            return jwt.encode(payload, DatabaseConfig.SECRET_KEY, algorithm='HS256')
        elif token_type == 'refresh':
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id,
                'token_type': 'refresh'
            }
            return jwt.encode(payload, DatabaseConfig.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def decode_auth_token(auth_token):
        return jwt.decode(auth_token, DatabaseConfig.SECRET_KEY, algorithms='HS256')


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    user_id = ma.auto_field()
    username = ma.auto_field()
    file_status = ma.auto_field()

