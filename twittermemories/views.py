from flask_restful import Resource
from flask import request,jsonify
from twittermemories.models import User, UserSchema
from twittermemories import db


class HelloWorld(Resource):

    def get(self):
        return {'hi': 'hello'}


class RegisterUser(Resource):
    def get(self):
        return {'word':'hee'}

    def post(self):
        # Catch username already taken error
        username = request.values.get('username')
        password = request.values.get('password')
        user_schema = UserSchema()
        new_user = User(username=username, raw_password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify(user_schema.dump(new_user))


class LoginUser(Resource):
    # TODO: Finish implementing the login function once I add JWT
    def get(self):
        username = request.values.get('username')
        password = request.values.get('password')
        user = User.query.filter_by(username=username).first()
        if user.check_password(password):
            return { 'response' : user.username + ' is now logged in'}
        else:
            return { 'response': 'INCORRECT PASSWORD'}
