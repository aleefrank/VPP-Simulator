from datetime import datetime
from hashlib import md5
from time import time

import json
import sqlalchemy
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import TypeDecorator
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from WebAppOptimizer.app import db, login


class JsonPickleType(TypeDecorator):
    impl = sqlalchemy.Text(256)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    configurations = db.relationship('Configuration', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Configuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    confname = db.Column(db.String(64), index=True)
    body = db.Column(JsonPickleType())
    timestamp = db.Column(db.DateTime, index=True, nullable=False, default=datetime.utcnow())
    datetime = db.Column(db.DateTime, index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Configuration - {}: {} Date: {} --- by {} {}>'.format(self.confname, self.body, self.datetime,
                                                                       self.user, self.timestamp)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.confname,
            'body': self.body,
            'date': self.datetime,
            'timestamp': self.timestamp
        }
