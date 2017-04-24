# coding=utf-8
from datetime import datetime
from time import time

from flask import current_app, g, jsonify, request
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from validators import url
from werkzeug.exceptions import NotFound
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.api.custom_exceptions import (ValidationException,
                                       UrlValidationException)
from app.api.errors import bad_request
from app.api.shortener import Shortener


class AnonymousUser(AnonymousUserMixin):
    @staticmethod
    def get_anonymous_user():
        anonymous_user = User.get_by_username("AnonymousUser")
        if anonymous_user:
            return anonymous_user
        return AnonymousUser.create_anonymous_user()

    @staticmethod
    def create_anonymous_user():
        anonymous_user = User(username='AnonymousUser', lastname="anonymous",
                              firstname='anonymous', email='anonymous')
        db.session.add(anonymous_user)
        db.session.commit()
        return anonymous_user

    @staticmethod
    def set_anonymous():
        if g.current_user.is_anonymous:
            g.current_user = AnonymousUser.get_anonymous_user()


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
    is_admin = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow())
    url = db.relationship("Url", secondary=user_url, backref='users',
                          lazy='dynamic')
    short_url = db.relationship("ShortenUrl",  backref='users',
                                lazy='dynamic')
    token = db.relationship("Token", backref="users", lazy="dynamic")

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
        return [s.now(), s.dumps({'id': self.id}).decode('ascii')]

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except BadSignature or SignatureExpired:
            return None
        if data["id"] == "AnonymousUser":
            return AnonymousUser()
        return User.query.get(data["id"])

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

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class ShortenUrl(db.Model):
    """
        Defines the shorten_url table schema and also handling
        shorten_url related functionalities.
    """
    __table_name__ = "shorten_urls"
    id = db.Column(db.Integer, primary_key=True)
    shorten_url_name = db.Column(db.String(20), unique=True, index=True,
                                 nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow())
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    long_url = db.Column(db.Integer, db.ForeignKey('url.id'))
    is_active = db.Column(db.Boolean, default=True)
    deleted = db.Column(db.Boolean, default=False)
    visits = db.relationship("ShortenUrlVisitLogs", backref='shorten_urls',
                             lazy='dynamic')

    @property
    def name(self):
        return request.url_root + self.shorten_url_name

    @name.setter
    def name(self, new_name):
        self.shorten_url_name = new_name

    @staticmethod
    def get_short_url_by_name(name):
        return ShortenUrl.query.filter_by(shorten_url_name=name).first()

    @staticmethod
    def save(shorten_url_name, user, long_url):
        shorten_url = ShortenUrl(shorten_url_name=shorten_url_name,
                                 user=user.id, long_url=long_url.id)
        db.session.add(shorten_url)
        db.session.commit()

    @staticmethod
    def check_vanity_string_availability(vanity_string):
        if g.current_user.is_anonymous and vanity_string:
            raise ValidationException("Only registered users are liable "
                                      "to use vanity string")
        elif ShortenUrl.get_short_url_by_name(vanity_string):
            raise ValidationException("The vanity string '{}' is already in "
                                      "use. Please input another vanity string"
                                      .format(vanity_string))

    def confirm_user(self):
        if self.user != g.current_user.id:
            raise NotFound

    def delete(self):
        if self.deleted:
            return bad_request("The shorten url has already been deleted")
        self.deleted = True
        db.session.commit()
        return jsonify({"message": "Successfully deleted"})

    def revert_delete(self):
        if not self.deleted:
            return bad_request("You can't revert deletion on a "
                               "shorten url that hasn't been deleted")
        self.deleted = False
        db.session.commit()
        return jsonify({"message": "Successfully reverted deletion"})

    def activate(self):
        if self.is_active:
            return bad_request("The shorten url is currently active")
        self.is_active = True
        db.session.commit()
        return jsonify({"message": "Successfully activated"})

    def deactivate(self):
        if not self.is_active:
            return bad_request("The shorten url is currently not active")
        self.is_active = False
        db.session.commit()
        return jsonify({"message": "Successfully deactivated"})

    @staticmethod
    def update_target_url(shorten_url, shorten_url_target, new_long_url):
        if Url.get_url_by_name(new_long_url):
            long_url = Url.get_url_by_name(new_long_url)
            if g.current_user in long_url.user:
                raise ValidationException("You already have a shorten url"
                                          " for the proposed long url."
                                          " Therefore the update failed")
            g.current_user.url.remove(shorten_url_target)
            if not shorten_url_target.user.count():
                shorten_url_target.delete()
            g.current_user.url.append(long_url)
            shorten_url.long_url = long_url.id
        elif shorten_url_target.user.count() == 1:
            shorten_url_target.name = new_long_url
        else:
            g.current_user.url.append(Url(url_name=new_long_url))
            db.session.commit()
            shorten_url.long_url = Url.get_url_by_name(new_long_url).id
        db.session.commit()

    @staticmethod
    def get_all_shorten_urls_by_dated_added():
        return ShortenUrl.query.order_by(db.desc(ShortenUrl.date_added))\
            .filter_by(is_active=True, deleted=False).all()

    @staticmethod
    def get_all_shorten_urls_by_popularity():
        return ShortenUrl.query.order_by(db.desc(ShortenUrl.number_of_visit))\
            .filter_by(is_active=True, deleted=False).all()


class Url(db.Model):
    """
    Defines the url table schema and also handling url related
    functionalities.
    """
    __table_name__ = "urls"
    id = db.Column(db.Integer, primary_key=True)
    url_name = db.Column(db.String(20), unique=True, index=True,
                         nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow())
    user = db.relationship("User", secondary=user_url, backref='urls',
                          lazy='dynamic')
    short_url = db.relationship("ShortenUrl", backref='urls',
                                lazy='dynamic')

    @property
    def name(self):
        return self.url_name

    @name.setter
    def name(self, new_url_name):
        self.url_name = new_url_name

    @property
    def get_id(self):
        return self.id

    @staticmethod
    def check_validity(new_url):
        if not url(new_url):
            raise UrlValidationException("Invalid url (Either url is empty"
                                         " or of invalid format. (Url must include"
                                         " either http:// or https://))")

    @staticmethod
    def get_from_json(json_data):
        return [
            Url(url_name=json_data['url']),
            json_data["vanity_string"]
            if "vanity_string" in json_data else None,
            json_data["shorten_url_length"]
            if "shorten_url_length"in json_data else None
        ]

    @staticmethod
    def get_url_by_name(url_name):
        return Url.query.filter_by(url_name=url_name).first()

    @staticmethod
    def get_shorten_url(new_url, vanity_string, short_url_length):
        existing_long_url = Url.get_url_by_name(new_url.name)
        if existing_long_url and existing_long_url in g.current_user.url:
            return ["Shorten Url already exist for this long url",
                    list(set(existing_long_url.short_url)
                         .intersection(g.current_user.short_url))[0]
                    ]
        shorten_url_name = Shortener.generate_shorten_name(short_url_length) \
            if not vanity_string else vanity_string
        while ShortenUrl.get_short_url_by_name(shorten_url_name):
            shorten_url_name = Shortener\
                                .generate_shorten_name(short_url_length)
        if existing_long_url and not(existing_long_url in g.current_user.url):
            Url.save(existing_long_url, shorten_url_name)
        else:
            Url.save(new_url, shorten_url_name)
        return ["Url successful shoretened",
                ShortenUrl.get_short_url_by_name(shorten_url_name)]

    @staticmethod
    def save(url, shorten_url_name):
        g.current_user.url.append(url)
        db.session.commit()
        ShortenUrl.save(shorten_url_name=shorten_url_name,
                        user=g.current_user, long_url=url)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_urls_by_dated_added():
        return Url.query.order_by(db.desc(Url.date_added)).all()


class ShortenUrlVisitLogs(db.Model):
    __tablename__ = 'shorten_url_visit_log'
    id = db.Column(db.Integer, primary_key=True)
    shorten_url = db.Column(db.Integer, db.ForeignKey('shorten_url.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow())
    ip_address = db.Column(db.String, nullable=False)
    port = db.Column(db.Integer)

    @staticmethod
    def create_visit_log_instance(shorten_url, remote_addr, port):
        shorten_url_visit = ShortenUrlVisitLogs(
            shorten_url=shorten_url,
            ip_address=remote_addr,
            port=port,
        )
        return shorten_url_visit



class Token(db.Model):
    __tablename__ = "token"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    creation_time = db.Column(db.Integer, nullable=False)
    expiration_time = db.Column(db.Integer, nullable=False)

    @staticmethod
    def check_existence_of_valid_token(user_id):
        """
        checks if a valid token exist in the database for a particular user
        whose user id is passed as argument.
        It returns the token if a valid one exists else None is returned
        :param user_id: 
        :return list or None: 
        """
        Token.delete_expired_token()
        token_instance = Token.query.filter_by(user=user_id).first()
        if token_instance:
            return [token_instance.creation_time, token_instance.token]

    @staticmethod
    def save(token_generated):
        """
        this function saves an instance of the token model into 
        the database
        :param token_generated
        :return: 
        """
        token_instance = Token(token=token_generated[1],
                               user=g.current_user.id,
                               creation_time=token_generated[0],
                               expiration_time=token_generated[0] + 3600)
        db.session.add(token_instance)
        db.session.commit()

    @staticmethod
    def delete_expired_token():
        """
        removes all expired token s from the database
        :return None: 
        """
        expired_tokens = Token.query.filter(Token.expiration_time <= time()).all()
        if expired_tokens:
            for token in expired_tokens:
                db.session.delete(token)
            db.session.commit()
