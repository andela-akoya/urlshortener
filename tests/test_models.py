# coding=utf-8
import os
import time
import unittest

from flask import g

from app import create_app, db
from app.api.custom_exceptions import ValidationException
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

    def test_password_is_hashed(self):
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
        tests the convert_json_to_user_object if it returns an object instance if json
        formatted data is passed in as argument
        """
        json_data = {
            'username': 'koyexes',
            'firstname': 'gabriel',
            'lastname': 'koya',
            'email': 'koyexes@gmail.com',
            'password': 'password'
        }

        self.assertIsInstance(User.convert_json_to_user_object(json_data), User)

    def test_get_from_json_for_data_allocation(self):
        """
        tests the convert_json_to_user_object if it properly allocates the right
        data to the appropriate object property
        """
        json_data = {
            'username': 'koyexes',
            'firstname': 'gabriel',
            'lastname': 'koya',
            'email': 'koyexes@gmail.com',
            'password': 'password'
        }

        user = User.convert_json_to_user_object(json_data)
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

    def test_delete_user(self):
        """
        tests the function if it removes the user record from
        the database
        """
        self.user.password = "password"
        db.session.add(self.user)
        db.session.commit()
        self.assertTrue(User.get_by_username("koyexes"))
        self.user.delete()
        self.assertFalse(User.get_by_username("koyexes"))


class UrlModelTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User(username="koyexes",lastname="koya",
                         firstname="gabriel",email="koyexes@gmail.com")
        self.url = Url(url_name="http://www.google.com")
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        g.current_user = self.user

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_url_name_property_getter(self):
        """
        tests the function if it returns the value of the
        url_name property
        """
        self.assertTrue(self.url.name == "http://www.google.com")

    def test_url_name_property_setter(self):
        """
        tests the function if it properly sets the value of the
        url_name property
        """
        self.assertTrue(self.url.name == "http://www.google.com")
        self.url.name = "http://www.facebook.com"
        self.assertNotEqual(self.url.name, "http://www.google.com")
        self.assertTrue(self.url.name == "http://www.facebook.com")

    def test_url_id_property_getter(self):
        """
        tests the function if it returns the value of the
        url_id property
        """
        self.assertFalse(self.url.get_id)
        db.session.add(self.url)
        db.session.commit()
        self.assertTrue(Url.get_url_by_name(self.url.name).get_id == 1)

    def test_check_url_validity_with_valid_url(self):
        """
        tests the function if it return a None for a
        valid url
        """
        self.assertEqual(Url.check_validity("http://www.facebook.com"), None)

    def test_check_url_validity_with_invalid_url(self):
        """
        tests the function if it raises a UrlValidationException if an
        invalid url is passed as argument
        """
        expected_output = ("Invalid url (Either url is empty or invalid."
                           " (Url must include either http:// or https://))")
        with self.assertRaises(ValidationException) as context:
            Url.check_validity("htt://web")
            self.assertEqual(expected_output, context.exception.message)

    def test_get_url_by_name(self):
        """
        tests the function if it returns a Url object from the database
        if an existing url name is passed as argument
        """
        db.session.add(self.url)
        db.session.commit()
        url = Url.get_url_by_name("http://www.google.com")
        self.assertEqual(url, self.url)

    def test_get_url_by_name_with_non_existing_url_name(self):
        """
        tests the function if it returns None if a non existing url name
        is passed as argument
        """
        db.session.add(self.url)
        db.session.commit()
        url = Url.get_url_by_name("http://www.jumia.com")
        self.assertEqual(url, None)

    def test_get_from_json(self):
        """
        tests the function if a list containing a url object, a vanity
        string, and a length is returned if a json formatted data containing
        a url_name, a vanity string and a length in integer is passed in as
        argument
        """
        json_data = {
            "url": "http://www.google.com",
            "vanity_string": "ggle75",
            "shorten_url_length": 6
        }
        output = Url.get_from_json(json_data)
        self.assertIsInstance(output, list)
        self.assertIsInstance(output[0], Url)
        self.assertEqual(output[1], "ggle75")

    def test_get_from_json_with_minimal_json_data(self):
        """
        tests the function if a list containing a url object, a None value
        for both vanity string and length is returned if a json formatted data
        containing only a url_name is passed in as argument
        """
        json_data = {"url": "http://www.google.com"}
        output = Url.get_from_json(json_data)
        self.assertIsNone(output[1])
        self.assertIsNone(output[2])
        self.assertIsInstance(output[0], Url)

    def test_get_shorten_url(self):
        """
        test the function if it returns a shorten url for the long url passed
        in as argument
        """
        output = Url.get_shorten_url(self.url, None, None)
        self.assertTrue(output)

    def test_get_shorten_url_for_instance(self):
        """
        test the function if the shorten url returned for the long url passed
        in as argument is an instance of the shortenUrl class
        """
        g.current_user = self.user
        output = Url.get_shorten_url(self.url, None, None)
        self.assertIsInstance(output, ShortenUrl)

    def test_get_shorten_url_with_vanity_string(self):
        """
        tests the function if it returns the vanity string passed in as
        argument as the shorten url rather than generating a short url
        """
        output = Url.get_shorten_url(self.url, "facebk", None)
        self.assertEqual(output.name.split("/")[-1], "facebk")

    def test_get_shorten_url_with_short_url_length(self):
        """
        tests the function if it returns a short url whose length is
        equal to the value of the short_url_length argument.
        """
        output = Url.get_shorten_url(self.url, None, 10)
        self.assertEqual(len(output.name.split("/")[-1]), 10)

    def test_delete_long_url(self):
        """
        tests the function if it removes the url record from
        the database
        """
        db.session.add(self.url)
        db.session.commit()
        self.assertTrue(Url.get_url_by_name("http://www.google.com"))
        self.url.delete()
        self.assertFalse(Url.get_url_by_name("http://www.google.com"))


class ShortenUrlModelTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User(username="koyexes",lastname="koya",
                         firstname="gabriel",email="koyexes@gmail.com")
        self.url = Url(url_name="http://www.google.com")
        self.short_url = ShortenUrl(shorten_url_name="pswd45")
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        g.current_user = self.user

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_short_url_name_property_getter(self):
        """
        tests the function if it returns the value of the
        short_url_name property
        """
        self.assertTrue(self.short_url.name.split("/")[-1] == "pswd45")

    def test_url_name_property_setter(self):
        """
        tests the function if it properly sets the value of the
        short_url_name property
        """
        self.assertTrue(self.short_url.name.split("/")[-1] == "pswd45")
        self.short_url.name = "anoda45"
        self.assertNotEqual(self.short_url.name, "pswd45")
        self.assertTrue(self.short_url.name.split("/")[-1] == "anoda45")

    def test_get_short_url_by_name(self):
        """
        tests the function if it returns the right short_url object from the
        database based on the short_url name passed in as argument
        """
        db.session.add(self.short_url)
        db.session.commit()
        output = ShortenUrl.get_short_url_by_name("pswd45")
        self.assertTrue(output == self.short_url)

    def check_vanity_string_availability_for_anonymous_user(self):
        """
        tests the check_vanity_string_availability if it flags a
        validation exception for anonymous user
        """
        g.current_user = AnonymousUser()
        expected_output = "Only registeredusers are liable to use " \
                          "vanity string"
        with self.assertRaises(ValidationException) as context:
            ShortenUrl.check_vanity_string_availability("pswd45")
            self.assertEqual(expected_output, context.exception.message)

    def test_delete_short_url(self):
        """
        tests the function if it removes the a shorten_url record from
        the database
        """
        db.session.add(self.short_url)
        db.session.commit()
        self.assertTrue(ShortenUrl.get_short_url_by_name("pswd45"))
        self.short_url.delete()
        self.assertFalse(Url.get_url_by_name("pswd45"))
