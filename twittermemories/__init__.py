from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from twittermemories.app_config import Config
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)

from twittermemories.views import RegisterUser, LoginUser, Feed, Refresh

# Endpoints
api.add_resource(LoginUser, '/LoginUser')
api.add_resource(RegisterUser, '/RegisterUser')
api.add_resource(Feed, '/Feed')
api.add_resource(Refresh, '/refresh')