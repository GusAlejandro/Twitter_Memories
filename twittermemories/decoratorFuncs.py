from jwt import ExpiredSignatureError, DecodeError
from functools import wraps
from twittermemories.models import User
from flask import request, g, jsonify


def access_token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get('authorization').split(" ")[1]
        try:
            payload = User.decode_auth_token(token)
            if payload['token_type'] == 'access':
                g.user = payload['sub']
                return fn(*args, **kwargs)
            else:
                # wrong token type, do not allow access to resource
                return jsonify({
                    'status': 'wrong token type'
                })
        except (ExpiredSignatureError, UnicodeDecodeError, DecodeError):
            # tell client the access token has expired and they need to request a new one using refresh token
            return jsonify({
                'status': 'expired access token, user is logged out'
            })
    return wrapper


def refresh_token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get('authorization').split(" ")[1]
        try:
            payload = User.decode_auth_token(token)
            if payload['token_type'] == 'refresh':
                g.user = payload['sub']
                return fn(*args, **kwargs)
            else:
                # wrong token type, do not allow access to resource
                return jsonify({
                    'status': 'wrong token type'
                })
        except (ExpiredSignatureError, UnicodeDecodeError, DecodeError):
            # tell client the access token has expired, force a log out. User must login in again
            return jsonify({
                'status': 'expired refresh token, user is logged out'
            })
    return wrapper

