from flask import Flask
from flask_restful import Api
from configuration.app_config import Config, TestConfig
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_cors import CORS


def create_app(config_file):
    app = Flask(__name__)
    app.config.from_object(config_file)
    api = Api(app)
    CORS(app)

    from twittermemories.models import db
    db.init_app(app)

    from twittermemories.views import RegisterUser, LoginUser, Feed, Refresh, FileUpload
    api.add_resource(LoginUser, '/login')
    api.add_resource(RegisterUser, '/register')
    api.add_resource(Feed, '/feed')
    api.add_resource(Refresh, '/refresh')
    api.add_resource(FileUpload, '/upload')

    return app


bcrypt = Bcrypt()
ma = Marshmallow()
app = create_app(Config)
bcrypt.init_app(app)
ma.init_app(app)


