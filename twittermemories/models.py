from flask_sqlalchemy import SQLAlchemy
from twittermemories import bcrypt, ma
from configuration.app_config import DatabaseConfig
import datetime
import jwt
import uuid

db = SQLAlchemy()


class Tweet(db.Model):
    __tablename__ = 'Tweet'
    tweet_id = db.Column(db.String, primary_key=True)
    tweet_text = db.Column(db.Text)
    user_id = db.Column(db.String(128), db.ForeignKey('User.user_id'), index=True)
    month = db.Column(db.Integer, index=True)
    day = db.Column(db.Integer)

    def __repr__(self):
        return self.user_id + ' tweed id: ' + self.tweet_id + ' month ' + self.month + ' day ' + self.day


class TweetSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Tweet

    tweet_id = ma.auto_field()
    month = ma.auto_field()


class User(db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.String(128), primary_key=True, unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashedPassword = db.Column(db.String(128))
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
        return bcrypt.generate_password_hash(raw_password)

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

