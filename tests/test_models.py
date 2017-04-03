# coding=utf-8
import os
import time
import unittest

from flask import g

from app import create_app, db
from app.api.custom_exceptions import (ValidationException,
                                       UrlValidationException)
from app.models import User, Url, ShortenUrl, AnonymousUser


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User(username="koyexes",lastname="koya",
                         firstname="gabriel",email="koyexes@gmail.com")
        self.user2 = User(username="admin",lastname="admin",
                         firstname="admin",email="admin@gmail.com")
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        """
        checks if password setter sets the password property
        appropriately based on the argument passed in.
        """
        self.user.password = "password"
        self.assertTrue(self.user.password_hash is not None)

    def test_hash_password(self):
        """tests if password supplied was really hashed."""
        self.user.password = "password"
        self.assertFalse(self.user.password_hash == "password")

    def test_no_password_getter(self):
        """
        tests the password getter if it raises the appropriate error
        when invoke
        """
        self.user.password = "password"
        with self.assertRaises(AttributeError):
            self.user.password

    def test_truthy_of_password_verification(self):
        """
        tests if  the true is returned for a correct password
        passed in as argument
        """
        self.user.password = "password"
        self.assertTrue(self.user.verify_password("password"))

    def test_falsy_of_password_verification(self):
        """
        tests if  the false is returned for a correct password
        passed in as argument
        """
        self.user.password = "password"
        self.assertFalse(self.user.verify_password("wrong_password"))

    def test_token_generation(self):
        """
        tests the token generation function if it generates
        encrypted and salted random strings
        """
        self.user.password = "password"
        self.assertTrue(self.user.generate_auth_token(3600))

    def test_password_salts_are_random(self):
        """
        tests if the salt used in hashing password is
        randomly generated.
        """
        user1 = User(password="password")
        user2 = User(password="password")
        self.assertFalse(
            user1.password_hash == user2.password_hash)

    def test_valid_verification_of_auth_token(self):
        """
        tests if the function genuinely test the validation of
        tokens generated
        """
        self.user.password = "password"
        db.session.add(self.user)
        db.session.commit()
        token = self.user.generate_auth_token(3600)
        self.assertTrue(User.verify_auth_token(token))

    def test_verification_for_actual_user(self):
        """
        tests the verification function if the user returned
        is the valid owner of the token
        """
        self.user.password = "password"
        db.session.add(self.user)
        db.session.commit()
        token = self.user.generate_auth_token(3600)
        self.assertEqual(User.verify_auth_token(token),  self.user)

    def test_invalid_verification_of_auth_token(self):
        """
        tests the authentication verification token if it
        invalidates and identifies wrong tokens
        """
        self.assertFalse(User.verify_auth_token(os.urandom(24)))

    def test_expired_token(self):
        """
        tests if the token verification function returns None for
        an expired token
        """
        self.user.password = 'password'
        db.session.add(self.user)
        db.session.commit()
        token = self.user.generate_auth_token(2)
        time.sleep(4)
        self.assertFalse(User.verify_auth_token(token))

    def test_get_by_username(self):
        """
        tests the get_by_username function if it returns the
        appropriate user from the database if a username is
        passed as argument
        """
        db.session.add(self.user)
        db.session.add(self.user2)
        db.session.commit()
        self.assertTrue(self.user == User.get_by_username("koyexes"))

    def test_get_by_username_with_invalid_username(self):
        """
           tests the get_by_username function if it returns the
           none  if an invalid username is passed as argument
           """
        db.session.add(self.user)
        db.session.add(self.user2)
        db.session.commit()
        self.assertFalse(User.get_by_username("android"))

    def test_get_by_email(self):
        """
        tests the get_by_email function if it returns the
        appropriate user from the database if an email is
        passed as argument
        """
        db.session.add(self.user)
        db.session.add(self.user2)
        db.session.commit()
        returned_user = User.get_by_email("koyexes@gmail.com")
        self.assertTrue(self.user == returned_user)

    def test_get_by_email_with_invalid_email(self):
        """
       tests the get_by_email function if it returns the
       none  if an invalid email is passed as argument
       """
        db.session.add(self.user)
        db.session.add(self.user2)
        db.session.commit()
        self.assertFalse(User.get_by_email("android@gmail.com"))


    def test_get_from_json(self):
        """
        tests the get_from_json if it returns an object instance if json
        formatted data is passed in as argument
        """
        json_data = {
            'username': 'koyexes',
            'firstname': 'gabriel',
            'lastname': 'koya',
            'email': 'koyexes@gmail.com',
            'password': 'password'
        }

        self.assertIsInstance(User.get_from_json(json_data), User)

    def test_get_from_json_for_data_allocation(self):
        """
        tests the get_from_json if it properly allocates the right
        data to the appropriate object property
        """
        json_data = {
            'username': 'koyexes',
            'firstname': 'gabriel',
            'lastname': 'koya',
            'email': 'koyexes@gmail.com',
            'password': 'password'
        }

        user = User.get_from_json(json_data)
        self.assertTrue(user.username == "koyexes")
        self.assertEqual(user.lastname, "koya")
        self.assertFalse(user.email == "password")

    def test_save(self):
        """
        tests the save function if it saves a User instance to the
        database
        """
        User.save(self.user)
        self.assertTrue(
            User.query.filter_by(username=self.user.username).first())

    def test_check_username_uniqueness(self):
        """
        expects the function to flag a validation exception if an already
        existing username in the database equals the username argument
        passed in
        """
        db.session.add(self.user)
        db.session.commit()
        with self.assertRaises(ValidationException) as context:
            User.check_username_uniqueness("koyexes")
            self.assertEqual("The username 'koyexes' already exist",
                             context.exception.message)

    def test_check_username_uniqueness_with_unique_username(self):
        """
        expects the function not to flag a validation exception if a non
        existing username is passed in as argument
        """
        db.session.add(self.user)
        db.session.commit()
        output = User.check_username_uniqueness("gabriel")
        self.assertNotEqual("The username 'koyexes' already exist",
                            output)

    def test_check_email_uniqueness(self):
        """
        expects the function to flag a validation exception if an already
        existing email in the database equals the email argument
        passed in
        """
        db.session.add(self.user)
        db.session.commit()
        with self.assertRaises(ValidationException) as context:
            User.check_email_uniqueness("koyexes@gmail.com")
            self.assertEqual("The username 'koyexes@gmail.com' already exist",
                             context.exception.message)