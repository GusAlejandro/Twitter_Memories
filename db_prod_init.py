from twittermemories import app
from twittermemories.models import User, Tweet, db

with app.app_context():
    db.create_all()