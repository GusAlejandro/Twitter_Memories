from twittermemories import db, bcrypt, ma

# TODO: Finalize model for User Class


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashedPassword = db.Column(db.String(128))

    def __init__(self, raw_password, **kwargs):
        super(User, self).__init__(**kwargs)
        self.hashedPassword = User.hash_password(raw_password)

    def __repr__(self):
        return self.username + ' with id: ' + str(self.id)

    @staticmethod
    def hash_password(raw_password):
        return bcrypt.generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.hashedPassword, raw_password)


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = ma.auto_field()
    username = ma.auto_field()
