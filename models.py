from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)

class User (db.Model):
    """ Table for the users of the site """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)

    username = db.Column(db.Text)

    password = db.Column(db.Text)

    posts = db.relationship('Message')

    @classmethod
    def signup(cls, username,password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Message(db.Model):
    """Posts on Ticker"""

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True,)

    title = db.Column(db.Text)

    ticker = db.Column(db.Text)

    text = db.Column(db.Text, nullable=False,)

    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    users = db.relationship('User')