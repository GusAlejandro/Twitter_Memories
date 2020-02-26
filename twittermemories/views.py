import os
from flask_restful import Resource
from flask import request, g, jsonify
from twittermemories.models import User, UserSchema
from twittermemories import db, storage_client
from sqlalchemy.exc import IntegrityError
from twittermemories.view_helper_funcs import access_token_required, refresh_token_required, is_allowed_file
from twittermemories.app_config import GCPConfig, Config
from werkzeug.utils import secure_filename


class RegisterUser(Resource):

    def post(self):
        username = request.values.get('username')
        password = request.values.get('password')
        user_schema = UserSchema()
        try:
            new_user = User(username=username, raw_password=password)
            db.session.add(new_user)
            db.session.commit()
            return jsonify(user_schema.dump(new_user))
        except IntegrityError:
            db.session.rollback()
            return jsonify({'Error': "Username is taken already"})


class LoginUser(Resource):

    def post(self):
        username = request.values.get('username')
        password = request.values.get('password')
        user = User.query.filter_by(username=username).first()
        if user.check_password(password):
            # if username/password combo is valid, generate token
            access_token = User.encode_auth_token(user.user_id, 'access')
            # TODO: Persist refresh token in db to handle logout server-side as well (ideally we would have entire seperate auth server)
            refresh_token = User.encode_auth_token(user.user_id, 'refresh')
            return jsonify({
                'access_token': access_token.decode('utf-8'),
                'refresh_token': refresh_token.decode('utf-8')
            })
        else:
            return { 'response': 'INCORRECT USERNAME + PASSWORD COMBINATION'}


class Refresh(Resource):
    """
    Receives refresh token and if valid, proceeds to generate a new access token, returns new access token
    """
    @refresh_token_required
    def post(self):
        # when we start storing the refresh token we need to add logic to check agaisnt the db
        return jsonify({
            'access_token': User.encode_auth_token(g.user, 'access').decode('utf-8')
        })


class Feed(Resource):

    @access_token_required
    def get(self):
        user_id = g.user
        user = User.query.filter_by(user_id=user_id).first()
        return {'file_status': user.file_status}


class FileUpload(Resource):

    @access_token_required
    def post(self):
        buckets = list(storage_client.list_buckets())
        if 'file' not in request.files:
            return jsonify({
                'error': 'File not received'
            })
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'error': 'no file selected'
            })
        if file and is_allowed_file(file.filename):
            # store file locally
            file.filename = g.user + '.json'
            filename = secure_filename(file.filename)
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))

            #uplaod file to GCP
            bucket = storage_client.bucket(GCPConfig.GCP_STORAGE_BUCKET)
            blob = bucket.blob(filename)
            blob.upload_from_filename(os.path.join(Config.UPLOAD_FOLDER, filename))

            # TODO: set user file_status to 1
            # TODO: delete the locally stored file

            return jsonify({
                'status': 'file uploaded successfully'
            })