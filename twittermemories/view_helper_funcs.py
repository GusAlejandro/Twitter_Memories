from jwt import ExpiredSignatureError, DecodeError
from functools import wraps
from twittermemories.models import User
from flask import request, g, make_response
from configuration.app_config import Config


def access_token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization').split(" ")[1]
        if not token or 'null' in token:
            return make_response({
                'Error': 'Request does not include token'
            }, 401)
        try:
            payload = User.decode_auth_token(token)
            if payload['token_type'] == 'access':
                g.user = payload['sub']
                return fn(*args, **kwargs)
            else:
                # wrong token type, do not allow access to resource
                return make_response({
                    'Error': 'wrong token type'
                }, 401)
        except (ExpiredSignatureError, UnicodeDecodeError, DecodeError):
            # tell client the access token has expired and they need to request a new one using refresh token
            return make_response({
                'Error': 'Access token has expired'
            }, 401)
    return wrapper


def refresh_token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization').split(" ")[1]
        try:
            payload = User.decode_auth_token(token)
            if payload['token_type'] == 'refresh':
                g.user = payload['sub']
                return fn(*args, **kwargs)
            else:
                # wrong token type, do not allow access to resource
                return make_response({
                    'Error': 'wrong token type'
                }, 401)
        except (ExpiredSignatureError, UnicodeDecodeError, DecodeError):
            # tell client the access token has expired, force a log out. User must login in again
            return make_response({
                'Error': 'Refresh token is expired, user has been logged out'
            }, 401)
    return wrapper


def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

