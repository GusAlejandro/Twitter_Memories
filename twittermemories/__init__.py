from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from twittermemories.app_config import Config
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from google.cloud import storage
from twittermemories.app_config import GCPConfig

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)
storage_client = storage.Client.from_service_account_json(GCPConfig.GCP_JSON)

from twittermemories.views import RegisterUser, LoginUser, Feed, Refresh, FileUpload

# Endpoints
api.add_resource(LoginUser, '/login')
api.add_resource(RegisterUser, '/register')
api.add_resource(Feed, '/feed')
api.add_resource(Refresh, '/refresh')
api.add_resource(FileUpload, '/upload')