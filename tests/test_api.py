# coding=utf-8
import json, time, unittest
from base64 import b64encode

from flask import url_for, g

from app import db, create_app
from app.models import User, AnonymousUser, Url, ShortenUrl



class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.user = User(username="koyexes", lastname="koya",
                         firstname="gabriel", email="koyexes@gmail.com",
                         is_admin=True)
        self.user2 = User(username="balrog", lastname="admin",
                         firstname="admin", email="admin@gmail.com")
        self.user.password = "password"
        self.user2.password = "admin"
        self.url1 = Url(url_name="http://www.google.com")
        self.url2 = Url(url_name="http://www.facebook.com")
        self.url3 = Url(url_name="http://www.twitter.com")
        db.session.add_all([self.user, self.user2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_403(self):
        """
        tests the 403 error function if it displays the right messages and
        status code when trying to access an endpoint with the wrong HTTP
        method
        """
        response = self.client.post(url_for('api.get_token'),
            headers=self.get_api_headers('email', 'password'))
        self.assertTrue(response.status_code == 405)
        json_response = json.loads(response.data.decode('utf-8'))
        error_message = " The method is not allowed for the requested URL."
        self.assertTrue(json_response['message'] == error_message)

    def test_404(self):
        """
        tests the 404 error function if it displays the right messages and
        status code when trying to access a wrong or non existing endpoint
        """
        response = self.client.get(
            '/wrong/url',
            headers=self.get_api_headers('email', 'password'))
        self.assertTrue(response.status_code == 404)
        json_response = json.loads(response.data.decode('utf-8'))
        error_message = "404 Not Found: The requested URL was not found " \
                        "on the server.  If you entered the URL manually" \
                        " please check your spelling and try again."
        self.assertTrue(json_response['message'] == error_message)

    def test_authentication_with_wrong_username(self):
        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('adigun', 'password'))
        self.assertTrue(response.status_code == 401)

    def test_authentication_with_wrong_password(self):
        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('koyexes', 'pwd'))
        self.assertTrue(response.status_code == 401)

    def test_anonymous(self):
        """
        tests if the appropriate status code and message is returned if
        an invalid token is used for authentication
        """
        response = self.client.get(url_for('api.get_token'),
                                   headers=self.get_api_headers('', ''))
        self.assertTrue(response.status_code == 401)
        self.assertIsInstance(g.current_user, AnonymousUser)

    def test_token_authentication_with_bad_token(self):
        response = self.client.get(url_for('api.get_token'),
                                   headers=self.get_api_headers('bad token', ''))
        self.assertTrue(response.status_code == 401)

    def test_token_authentication_with_expired_token(self):
        """
        tests if the appropriate status code and message is returned if
        an expired token is used for authentication
        """
        token = self.user.generate_auth_token(2)
        time.sleep(4)
        response = self.client.get(url_for('api.get_token'),
                                   headers=self.get_api_headers(token, ''))
        self.assertTrue(response.status_code == 401)
        response_message = json.loads(response.data.decode('utf-8'))['message']
        self.assertTrue(response_message == "invalid credentials")

    def test_get_token(self):
        """
        tests if a token is generated when the endpoint /api/token is
        reached with valid authentication credentials
        """
        response = self.client.get(url_for('api.get_token'),
                                   headers=self.get_api_headers('koyexes',
                                                                'password'))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(json_response['token'])
        self.assertTrue(json_response['message'] ==
                        "Authentication successful")

    def test_non_json_content_type(self):
        """
        tests for appropriate error response when a non json content
        type is sent to the api
        """
        headers = self.get_api_headers("koyexes", "password")
        headers['Content-Type'] = ""
        response = self.client.post(url_for('api.register'),
                                    headers=headers, data="")
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 400)
        self.assertTrue(json_response['message'] ==
                        "Only json inputs are acceptable")

    def test_non_json_data(self):
        """
        tests for appropriate error response when a non json data
         is sent to the api
        """
        headers = self.get_api_headers("koyexes", "password")
        response = self.client.post(url_for('api.register'),
                                    headers=headers, data="non json data")
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 400)
        self.assertTrue(json_response['message'] ==
                        "The inputted data is not in json format")

    def test_empty_json_data(self):
        """
        tests for appropriate error response when an empty json data
         is sent to the api
        """
        headers = self.get_api_headers("koyexes", "password")
        response = self.client.post(url_for('api.register'),
                                    headers=headers, data="")
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 400)
        self.assertTrue(json_response['message'] ==
                        "Empty data are not acceptable")

    def test_json_data_with_invalid_keys(self):
        """
        tests for appropriate error response when a json data with
        invalid keys is sent to the api
        """
        data = json.dumps({"username": "adekunle", "age": 25})
        headers = self.get_api_headers("", "")
        response = self.client.post(url_for('api.register'),
                                    headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 400)
        self.assertTrue(json_response['message'] ==
                        "The following {'age'} are not valid keys")

    def test_json_data_key_with_empty_value(self):
        """
        tests for appropriate error message if a json data containing
        keys without value is sent to the api
        """
        data = json.dumps({"username": "", "password": "pwd"})
        headers = self.get_api_headers("", "")
        response = self.client.post(url_for('api.register'),
                                    headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 400)
        self.assertTrue(json_response['message'] ==
                        "username can't be empty")

    def test_registration(self):
        """
        test the registration endpoint if it returns the appropriate
        error if an existing username is used for registration
        """
        data = json.dumps(
            {"username": "admin", "password": "pwd",
             "confirm_password": "pwd", "lastname": "admin",
             "firstname": "admin", "email": "admin@noreply.com"})
        headers = self.get_api_headers("", "")
        response = self.client.post(url_for('api.register'),
                                    headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 201)
        self.assertTrue(json_response['message'] ==
                        "Successfully Registered")
        self.assertTrue(User.query.filter_by(username="admin").first())

    def test_registration_password_equality(self):
        """
        tests the registration endpoint if it returns appropriate
        error message if the password and confirm_password key values don't
        match
        """

        data = json.dumps({"username": "admin", "password": "password",
                           "confirm_password": "pwd", "lastname": "admin",
                           "firstname": "admin", "email": "admin@noreply.com"})
        headers = self.get_api_headers("", "")
        response = self.client.post(url_for('api.register'), headers=headers,
                                    data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 400)
        self.assertTrue(json_response['message'] == "Passwords don't match")

    def test_get_urls_for_particular_user(self):
        """
        tests the get_urls endpoint if it returns a list of all the long urls
        have been shortened for a particular user
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        g.current_user.url.append(self.url2)
        g.current_user.url.append(self.url3)
        db.session.commit()
        headers = self.get_api_headers("koyexes", "password")
        response = self.client.get(url_for('api.get_urls_for_particular_user'),
                                   headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(json_response["url_list"], list)
        self.assertEqual(len(json_response["url_list"]), 3)

    def test_get_shorten_urls_for_particular_user(self):
        """
        tests the get_shorten_urls endpoint if it returns a list of all the
        shorten urls of a particular person
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        ShortenUrl.save(shorten_url_name="1Qewt4", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        ShortenUrl.save(shorten_url_name="re234e", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        headers = self.get_api_headers("koyexes", "password")
        response = self.client.get(
            url_for('api.get_short_urls_for_particular_user'),headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(json_response["shorten_url_list"], list)
        self.assertEqual(len(json_response["shorten_url_list"]), 3)

    def test_shorten_long_url(self):
        """
        test the shorten long url endpoint if it returns a shorten url
        of the long url passed as post data
        """
        data = json.dumps({"url": "https://www.google.com"})
        headers = self.get_api_headers("", "")
        response = self.client.post(url_for('api.generate_shorten_url'),
                                    headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 201)
        self.assertTrue(json_response['shorten_url_name'])
        self.assertEqual(len(json_response['shorten_url_name']), 6)

    def test_shorten_existing_long_url(self):
        """
        test the shorten long url endpoint if it just shorten an existing
        long url rather saving the long url again in the database
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(Url(url_name="http://www.google.com"))
        db.session.commit()
        data = json.dumps({"url": "http://www.google.com"})
        headers = self.get_api_headers("", "")
        response = self.client.post(url_for('api.generate_shorten_url'),
                                    headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 201)
        self.assertTrue(json_response['shorten_url_name'])
        self.assertEqual(
            Url.query.filter_by(url_name="http://www.google.com").count(), 1)

    def test_shorten_long_url_with_vanity_string(self):
        """
        test the shorten long url endpoint if it returns the vanity string
         as shorten url of the long url passed as post data
        """
        data = json.dumps({"url": "https://www.google.com",
                           "vanity_string": "ggle123"})
        headers = self.get_api_headers("koyexes", "password")
        response = self.client.post(url_for('api.generate_shorten_url'),
                                    headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 201)
        self.assertTrue(json_response['shorten_url_name'] == "ggle123")

    def test_shorten_long_url_with_vanity_string_for_anonymous(self):
        """
        test the shorten long url endpoint if it returns appropriate
        error if vanity string is sent by an anonymous user
        """
        data = json.dumps({"url": "https://www.google.com",
                           "vanity_string": "ggle123"})
        headers = self.get_api_headers("", "")
        response = self.client.post(url_for('api.generate_shorten_url'),
                                    headers=headers, data=data)
        expected_output = "Only registered users are liable to use" \
                          " vanity string"
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 400)
        self.assertTrue(json_response['message'] == expected_output)

    def test_shorten_long_url_with_shorten_url_length(self):
        """
        test the shorten long url endpoint if it returns the length of the
         shorten url returned is equal to the shorten_url_length passed
         through the data
        """
        data = json.dumps({"url": "https://www.google.com",
                           "shorten_url_length": 4})
        headers = self.get_api_headers("koyexes", "password")
        response = self.client.post(url_for('api.generate_shorten_url'),
                                    headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 201)
        self.assertTrue(len(json_response['shorten_url_name']) == 4)

    def test_shorten_long_url_with_non_valid_url(self):
        """
        test the shorten long url endpoint if it returns appropriate error
        when an invalid url is passed as data
        """
        data = json.dumps({"url": ".com"})
        headers = self.get_api_headers("koyexes", "password")
        response = self.client.post(url_for('api.generate_shorten_url'),
                                    headers=headers, data=data)
        expected_output = "Invalid url (Either url is empty or invalid." \
                          " (Url must include either http:// or https://))"
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 400)
        self.assertTrue(json_response['message'] == expected_output)

    def test_get_urls(self):
        """
        tests the get_urls endpoint if it returns a list of all the long urls
        that has been shortened
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        g.current_user.url.append(self.url2)
        g.current_user.url.append(self.url3)
        db.session.commit()
        headers = self.get_api_headers("koyexes", "password")
        response = self.client.get(url_for('api.get_urls'), headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(json_response["url_list"], list)
        self.assertEqual(len(json_response["url_list"]), 3)

    def test_get_shorten_urls(self):
        """
        tests the get_shorten_urls endpoint if it returns a list of all the
        shorten urls
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        ShortenUrl.save(shorten_url_name="1Qewt4", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        ShortenUrl.save(shorten_url_name="re234e", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        headers = self.get_api_headers("koyexes", "password")
        response = self.client.get(
            url_for('api.get_shorten_urls'), headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(json_response["shorten_url_list"], list)
        self.assertEqual(len(json_response["shorten_url_list"]), 3)

    def test_get_long_url_with_shorten_url_id(self):
        """
        tests if the appropriately mapped long url is returned based on the
        shorten url's id passed in as argument
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        shorten_url_id = ShortenUrl.get_short_url_by_name("pwdse2").id
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-url/{}/url'.format(shorten_url_id)
        response = self.client.get(url, headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(json_response['url_name'] == "http://www.google.com")

    def test_get_long_url_with_invalid_shorten_url_id(self):
        """
        tests if the appropriately error message is returned based on the
        an invalid shorten url's id passed in as argument
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-url/{}/url'.format(3)
        response = self.client.get(url, headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        expected_output = "Requested resource was not found"
        self.assertTrue(response.status_code == 404)
        self.assertTrue(json_response['message'] == expected_output)

    def test_get_long_url_with_shorten_url_name(self):
        """
        tests if the appropriately mapped long url is returned based on the
        shorten url's name passed in as argument
        """

        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        shorten_url_name = ShortenUrl.get_short_url_by_name("pwdse2").shorten_url_name
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-url/{}/url'.format(shorten_url_name)
        response = self.client.get(url, headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(json_response['url_name'] == "http://www.google.com")

    def test_get_long_url_with_invalid_shorten_url_name(self):
        """
        tests if the appropriately error message is returned based on the
        an invalid shorten url name passed in as argument
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-url/{}/url'.format("pwresq")
        response = self.client.get(url, headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        expected_output = "Requested resource was not found"
        self.assertTrue(response.status_code == 404)
        self.assertTrue(json_response['message'] == expected_output)

    def test_activate_an_active_shorten_url(self):
        """
        tests if the appropriately error message is returned if an already
        active shorten_url is attempted to be activated
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        shorten_url_id = ShortenUrl.get_short_url_by_name("pwdse2").id
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-urls/{}/activate'.format(shorten_url_id)
        response = self.client.put(url, headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        expected_output = "The shorten url is currently active"
        self.assertTrue(response.status_code == 400)
        self.assertTrue(json_response['message'] == expected_output)

    def test_activate_shorten_url(self):
        """
        tests the route if it successfully activates an inactive
        shorten_url
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        shorten_url = ShortenUrl.get_short_url_by_name("pwdse2")
        shorten_url.deactivate()
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-urls/{}/activate'.format(shorten_url.id)
        response = self.client.put(url, headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(json_response['message'] == "Successfully activated")

    def test_deactivate_shorten_url(self):
        """
        tests the route if it successfully deactivates an active
        shorten_url
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        shorten_url = ShortenUrl.get_short_url_by_name("pwdse2")
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-urls/{}/deactivate'.format(shorten_url.id)
        response = self.client.put(url, headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(json_response['message'] == "Successfully "
                                                    "deactivated")

    def test_deactivate_an_inactive_shorten_url(self):
        """
        tests if the appropriately error message is returned if an already
        inactive shorten_url is attempted to be deactivated
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        shorten_url = ShortenUrl.get_short_url_by_name("pwdse2")
        shorten_url.deactivate()
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-urls/{}/deactivate'.format(shorten_url.id)
        response = self.client.put(url, headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 400)
        self.assertTrue(json_response['message'] == "The shorten url is"
                                                    " currently not active")

    def test_active_deactivate_shorten_url_by_anonymous_user(self):
        """
        tests if the appropriate error will be returned when an
        anonymous user tries to activate or deactivate a shorten url
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=Url.get_url_by_name(self.url1.name))
        shorten_url = ShortenUrl.get_short_url_by_name("pwdse2")
        headers = self.get_api_headers("", "")
        url = '/api/v1.0/shorten-urls/{}/deactivate'.format(shorten_url.id)
        response = self.client.put(url, headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 403)
        self.assertTrue(json_response['message'] == "You are not authorized"
                                                    " to use this service")

    def test_deactivate_or_activate_invalid_shorten_url(self):
        """
        tests if the appropriately error message is returned if a shorten_url
        is attempted to be deactivated or activated with invalid or
        non existing shorten_url id passed as argument.
        """
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-urls/{}/deactivate'.format(3)
        response = self.client.put(url, headers=headers)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 404)
        self.assertTrue(json_response['message'] == "The resource you seek to"
                                                    " update doesn't exist")

    def test_update_shorten_url_target(self):
        """
        tests if a shorten_url mapped target long_url is properly updated
        to a new long_url passed in thorough the request data
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        long_url = Url.get_url_by_name(self.url1.name)
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=long_url)
        shorten_url = ShortenUrl.get_short_url_by_name("pwdse2")
        data = json.dumps({"url": "http://www.change.com"})
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-urls/{}/url/update'.format(shorten_url.id)
        response = self.client.put(url, headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(json_response["long_url"] == "http://www.change.com")

    def test_update_shorten_url_target_with_invalid_id(self):
        """
        tests if appropriate error messages will be returned when an invalid
        short_url id is passed as argument
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        long_url = Url.get_url_by_name(self.url1.name)
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=long_url)
        data = json.dumps({"url": "http://www.change.com"})
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-urls/{}/url/update'.format(4)
        response = self.client.put(url, headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 404)
        self.assertTrue(json_response["message"] == "Requested resource"
                                                    " was not found")

    def test_update_shorten_url_target_invalid_url_format(self):
        """
        tests if appropriate error messages will be returned when an invalid
        short_url format is passed as data
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        long_url = Url.get_url_by_name(self.url1.name)
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=long_url)
        shorten_url = ShortenUrl.get_short_url_by_name("pwdse2")
        data = json.dumps({"url": "www.change"})
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-urls/{}/url/update'.format(shorten_url.id)
        response = self.client.put(url, headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        expected_output = "Invalid url (Either url is empty or invalid." \
                          " (Url must include either http:// or https://))"
        self.assertTrue(response.status_code == 400)
        self.assertTrue(json_response["message"] == expected_output)

    def test_update_shorten_url_target_with_empty_data(self):
        """
        tests if appropriate error messages will be returned when an empty
        value is passed as data
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        long_url = Url.get_url_by_name(self.url1.name)
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=long_url)
        shorten_url = ShortenUrl.get_short_url_by_name("pwdse2")
        data = json.dumps({"url": ""})
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-urls/{}/url/update'.format(shorten_url.id)
        response = self.client.put(url, headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 400)
        self.assertTrue(json_response["message"] == "url can't be empty")

    def test_update_shorten_url_target_with_owned_existing_long_url(self):
        """
        tests if appropriate error messages will be returned when updating
        a shorten_url target with a long_url that has already been shortened
        by the user
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        db.session.commit()
        long_url = Url.get_url_by_name(self.url1.name)
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=long_url)
        shorten_url = ShortenUrl.get_short_url_by_name("pwdse2")
        data = json.dumps({"url": "http://www.google.com"})
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-urls/{}/url/update'.format(shorten_url.id)
        response = self.client.put(url, headers=headers, data=data)
        expected_output = "You already have a shorten url for the proposed" \
                          " long url. Therefore the update failed"
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 400)
        self.assertTrue(json_response["message"] == expected_output)

    def test_update_shorten_url_target_with_existing_long_url(self):
        """
        tests if the update endpoint updates the target with an existing
        long_url passed in as argument if the user hasn't shortened the
        existing url before rather than create another one
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        User.get_by_username("balrog").url.append(self.url2)
        db.session.commit()
        long_url = Url.get_url_by_name(self.url1.name)
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=long_url)
        shorten_url = ShortenUrl.get_short_url_by_name("pwdse2")
        data = json.dumps({"url": self.url2.url_name})
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-urls/{}/url/update'.format(shorten_url.id)
        response = self.client.put(url, headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(json_response["long_url"] == self.url2.url_name)
        self.assertEqual(
            Url.query.filter_by(url_name=self.url2.url_name).count(), 1)

    def test_update_shorten_url_target_not_owned(self):
        """
        tests if a 404 message will be returned if a user tries
        to update the target of a shorten_url belonging to another user
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        User.get_by_username("balrog").url.append(self.url2)
        db.session.commit()
        long_url = Url.get_url_by_name(self.url1.name)
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=long_url)
        shorten_url = ShortenUrl.get_short_url_by_name("pwdse2")
        data = json.dumps({"url": self.url2.url_name})
        headers = self.get_api_headers("balrog", "admin")
        url = '/api/v1.0/shorten-urls/{}/url/update'.format(shorten_url.id)
        response = self.client.put(url, headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(response.status_code == 404)
        self.assertTrue(json_response["message"] == "Requested resource was"
                                                    " not found")

    def test_update_shorten_url_target_create_new_long_url(self):
        """
        tests if a new long_url will be created as target for the shorten_url
        """
        g.current_user = User.get_by_username("koyexes")
        g.current_user.url.append(self.url1)
        User.get_by_username("balrog").url.append(self.url1)
        db.session.commit()
        long_url = Url.get_url_by_name(self.url1.name)
        ShortenUrl.save(shorten_url_name="pwdse2", user=g.current_user,
                        long_url=long_url)
        shorten_url = ShortenUrl.get_short_url_by_name("pwdse2")
        data = json.dumps({"url": "https://www.change.com"})
        headers = self.get_api_headers("koyexes", "password")
        url = '/api/v1.0/shorten-urls/{}/url/update'.format(shorten_url.id)
        response = self.client.put(url, headers=headers, data=data)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(Url.query.filter_by(url_name="https://www.change.com"))
        self.assertTrue(json_response["long_url"] == "https://www.change.com" )







