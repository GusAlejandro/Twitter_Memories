import os
import json
from flask_restful import Resource
from flask import request, g, jsonify, make_response
from twittermemories.models import User, UserSchema, Tweet, TweetSchema, db
from google.cloud import storage
from configuration.app_config import GCPConfig
from sqlalchemy.exc import IntegrityError
from twittermemories.view_helper_funcs import access_token_required, refresh_token_required, is_allowed_file
from configuration.app_config import GCPConfig, Config
from werkzeug.utils import secure_filename
from celeryworker.tasks import process_tweets

storage_client = storage.Client.from_service_account_json(GCPConfig.GCP_JSON)


class RegisterUser(Resource): 

    """
    endpoint: /register
    parameters: 
        - username
        - password
    """

    def post(self):
        username = request.get_json().get('username')
        password = request.get_json().get('password')
        user_schema = UserSchema()
        try:
            new_user = User(username=username, raw_password=password)
            db.session.add(new_user)
            db.session.commit()
            return make_response(user_schema.dump(new_user), 200)
        except IntegrityError:
            db.session.rollback()
            return make_response({'Error': "Username is already taken."}, 403)


class LoginUser(Resource):

    # TODO: Refactor responses to incldue error codes like /register

    """
    endpoint: /login
    parameters:
        - username
        - password
    """

    def post(self):
        username = request.get_json().get('username')
        password = request.get_json().get('password')
        user = User.query.filter_by(username=username).first()

        if not user: 
            return make_response({'Error': 'Username and password combination is incorrect.'}, 403) 

        if user.check_password(password):
            # if username/password combo is valid, generate tokens
            access_token = User.encode_auth_token(user.user_id, 'access')
            # TODO: Persist refresh token in db to handle logout server-side as well (ideally we would have entire seperate server for auth)
            refresh_token = User.encode_auth_token(user.user_id, 'refresh')
            return make_response({
                'access_token': access_token.decode('utf-8'),
                'refresh_token': refresh_token.decode('utf-8')
                }, 200)
        else:
            return make_response({'Error': 'Username and password combination is incorrect.'}, 403)


class Refresh(Resource):
    """
    Receives refresh token and if valid, proceeds to generate a new access token, returns new access token
    """
    @refresh_token_required
    def post(self):
        # when we start storing the refresh token we need to add logic to check agaisnt the db
        return make_response({
            'access_token': User.encode_auth_token(g.user, 'access').decode('utf-8')
        }, 200)


class Feed(Resource):
    # TODO: Update to now return the tweets instead of the file status
    # TODO: Add in parameter comment 
    # TODO: write tests for this, setup script to populate db with data

    @access_token_required
    def get(self):
        month = request.get_json().get('month')
        date = request.get_json().get('date')
        # TODO: add in checks to see if month and date parameters were in the request
        user_id = g.user
        user = User.query.filter_by(user_id=user_id).first()
        tweet_query = Tweet.query.filter_by(user_id=user_id, month=month, day=date).all()
        tweet_list = list(map(lambda tweet: tweet.tweet_id, tweet_query))
        return make_response({'file_status': user.file_status, 'tweets': tweet_list}, 200)
    

class FileUpload(Resource):
    # TODO: Add in parameter comment
    # TODO: Currently testing and prod are using the same Google Cloud Storage Bucket
    # TODO: look into how to test this, adding configs for testing

    @access_token_required
    def post(self):
        if 'file' not in request.files:
            return make_response({
                'Error': 'File not received'
            }, 400)
        
        file = request.files['file']
        if file.filename == '' or not is_allowed_file(file.filename):
            return make_response({
                'Errpr': 'Invalid File Format. You must submit the tweet.js file from your Twitter archive.'
            }, 400)

        if file and is_allowed_file(file.filename):
            # store file locally
            file.filename = g.user + '.json'
            filename = secure_filename(file.filename)
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))

            # upload file to GCP
            bucket = storage_client.bucket(GCPConfig.GCP_STORAGE_BUCKET)
            blob = bucket.blob(filename)
            blob.upload_from_filename(os.path.join(Config.UPLOAD_FOLDER, filename))

            # update user file status
            user = User.query.filter_by(user_id=g.user).first()
            user.file_status = 1
            db.session.commit()

            # delete file from temp file storage
            os.remove(os.path.join(Config.UPLOAD_FOLDER, filename))

            # queue archive processing task
            process_tweets.delay(g.user)

            return make_response({
                'Status': 'File uploaded successfully'
            }, 200)

