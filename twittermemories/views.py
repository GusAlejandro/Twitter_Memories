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
    # TODO: Finish implementing the login function once I add JWT
    def post(self):
        username = request.values.get('username')
        password = request.values.get('password')
        user = User.query.filter_by(username=username).first()
        if user.check_password(password):
            return { 'response' : user.username + ' is now logged in'}
        else:
            return { 'response': 'INCORRECT USERNAME + PASSWORD COMBINATION'}
