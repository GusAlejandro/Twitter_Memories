from flask_restful import Resource
from flask import request,jsonify
from twittermemories.models import User, UserSchema
from twittermemories import db
from sqlalchemy.exc import IntegrityError


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
    # TODO: Implement Refresh Tokes
    def post(self):
        username = request.values.get('username')
        password = request.values.get('password')
        user = User.query.filter_by(username=username).first()
        if user.check_password(password):
            auth_token = user.encode_auth_token(user.user_id)
            return jsonify({
                'auth_token': auth_token.decode('utf-8')
            })
        else:
            return { 'response': 'INCORRECT USERNAME + PASSWORD COMBINATION'}


class Feed(Resource):

    def get(self):
        try:
            # TODO: adapt to refactored decode method
            # TODO: we can create a seperate method to handle veriufying acesss to protected resources, add in refresh token logic there in the future
            user_id = User.decode_auth_token(request.headers.get('authorization').split(" ")[1])
            user = User.query.filter_by(user_id=user_id).first()
            return {'file_status': user.file_status}
        except:
            return {'error': 'Token is off my dude'}