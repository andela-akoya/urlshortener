# coding=utf-8
from flask import current_app, g
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from validators import url, ValidationFailure
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.api.custom_exceptions import (ValidationException,
                                       UrlValidationException)
from app.api.shortener import Shortener


class AnonymousUser(AnonymousUserMixin):
    @staticmethod
    def get_anonymous_user():
        anonymous_user = User.get_by_username("Anonymous")
        if anonymous_user:
            return anonymous_user
        return AnonymousUser.create_anonymous_user()

    @staticmethod
    def create_anonymous_user():
        anonymous_user = User(username='Anonymous', lastname="anonymous",
                              firstname='anonymous', email='anonymous')
        db.session.add(anonymous_user)
        db.session.commit()
        return anonymous_user


user_url = db.Table('user_url',
                    db.Column('user_id', db.Integer,
                              db.ForeignKey('users.id')),
                    db.Column('urls_id', db.Integer,
                              db.ForeignKey('url.id')))


class User(db.Model, UserMixin):
    """
    Defines the user table schema and also handling user related
    functionalities.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True,
                         nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    firstname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128))
    url = db.relationship("Url", secondary=user_url, backref='users',
                          lazy='dynamic')
    short_url = db.relationship("ShortenUrl",  backref='users',
                                lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @property
    def url_list(self):
        return self.url

    @property
    def short_url_list(self):
        return self.short_url

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except BadSignature or SignatureExpired:
            return None
        user = User.query.get(data["id"])
        return user

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_from_json(json_data):
        return User(username=json_data["username"],
                    lastname=json_data["lastname"],
                    firstname=json_data["firstname"],
                    email=json_data["email"],
                    password=json_data["password"])

    @staticmethod
    def save(user):
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def check_username_uniqueness(username):
        if User.get_by_username(username):
            raise ValidationException("The username '{}' already exist"
                                      .format(username))

    @staticmethod
    def check_email_uniqueness(email):
        if User.get_by_email(email):
            raise ValidationException("The email '{}' already exist"
                                      .format(email))
