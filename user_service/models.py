import os

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from passlib.hash import bcrypt

from user_service.application import app

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    """
    User model.
    """
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = self.hash_password(password)

    def hash_password(self, plain_text_passwd):
        return bcrypt.hash(plain_text_passwd)

    def verify_password(self, plain_text_passwd):
        return bcrypt.verify(plain_text_passwd, self.password)

    def __repr__(self):
        return '<User %r>' % self.username
