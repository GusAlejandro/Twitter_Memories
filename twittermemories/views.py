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
        - username: str
        - password: str
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
    """
    endpoint: /login
    parameters:
        - username: str
        - password: str
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
    endpoint: /refresh
    """
    @refresh_token_required
    def post(self):
        # when we start storing the refresh token we need to add logic to check agaisnt the db
        return make_response({
            'access_token': User.encode_auth_token(g.user, 'access').decode('utf-8')
        }, 200)


class Feed(Resource):
    """
    endpoint: /feed
    parameters:
        - month: str
        - date: int
    """
    # TODO: write tests for this, setup script to populate db with data

    @access_token_required
    def get(self):
        month = request.get_json().get('month')
        date = request.get_json().get('date')

        if not month or not date:
            return make_response({'Error': 'Missing Request Parameters'}, 400)
    
        user_id = g.user
        user = User.query.filter_by(user_id=user_id).first()
        
        # Query uses composite index of Tweet.user_id + Tweet.month that we set up in the model definition  
        tweet_query = Tweet.query.filter_by(user_id=user_id, month=month, day=date).all()
        tweet_list = list(map(lambda tweet: tweet.tweet_id, tweet_query))
        return make_response({'file_status': user.file_status, 'tweets': tweet_list}, 200)
    

class FileUpload(Resource):
    """
    endpooint: /upload
    parameters:
        - file
    """
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

