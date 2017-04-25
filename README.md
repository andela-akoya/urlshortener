[![Build Status](https://travis-ci.org/andela-akoya/urlshortener.svg?branch=front-end-design)](https://travis-ci.org/andela-akoya/urlshortener)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/andela-akoya/urlshortener/badges/quality-score.png?b=front-end-design)](https://scrutinizer-ci.com/g/andela-akoya/urlshortener/?branch=front-end-design)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage Status](https://coveralls.io/repos/github/andela-akoya/urlshortener/badge.svg?branch=front-end-design)](https://coveralls.io/github/andela-akoya/urlshortener?branch=front-end-design)
# Nitly
Nitly is a REST API that allows users to shorten long urls into nicely formatted short URLs that can be customized using a user's vanity string of choice and also has the option of specifying the desired length of the short url. 
This repository contains a fully working API project that communicates seamlessly with the UrlShortener service. This API accepts only `JSON` objects as input. The API service requires authentication for easy access to the resources provided.

## Development
* [Flask](http://flask.pocoo.org/) - Flask is a BCD licensed microframework for Python based on Werkzeug and Jinja 2.
* [Flasl-HTTPAuth](https://flask-httpauth.readthedocs.io/en/latest/) - This is a simple extension that simplifies the use of HTTP authentication with Flask routes.
* [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) - This an extension that handles SQLAlchemy database migrations for Flask applications using Alembic. The database operations are made available through the Flask command-line interface.
* [Flask-Script](https://flask-script.readthedocs.io/en/latest/) - This extension provides support for writing external scripts in Flask. This includes running a development server, a customized Python shell, scripts to set up a database and other command-line tasks that belong outside the web application itself.
* [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.1/) - This extension help to simplify using SQLAlchemy with Flask by providing useful defaults and extra helpers that make it easier to accomplish common tasks.
* [Flask-WTF (Validator)](http://wtforms.readthedocs.io/en/latest/validators.html) - This a WTForms class that simply takes an input, verifies it fulfills some criterion, such as a maximum length for a string and returns. Or, if the validation fails, raises a ValidationError.
* [Flask-Inputs](http://pythonhosted.org/Flask-Inputs/) - This extension adds support for WTForms to validate request data from args to headers to json.
* [Python-Env](https://github.com/mattseymour/python-env) - This library allows the saving of environment variables in .env and loaded when the application runs.

## Application Features
###### User Authentication
Users are authenticated and validated using an `itsdangerous` token. Generating tokens on login ensures each account is unique to a user and can't be accessed by an authenticated user.

## Installation
1. Start up your terminal (or Command Prompt on Windows OS).
2. Ensure that you've `python` installed on your PC.
3. Clone the repository by entering the command `https://github.com/andela-akoya/urlshortener.git` in the terminal.
4. Navigate to the project folder using `cd into the project folder` on your terminal (or command prompt)
5. After cloning, create a virtual environment then install the requirements with the command:
`pip install -r requirements.txt`.
6. Create a `.env` file in your root directory as described in `.env.sample` file. Variables such as DATABASE_URL and config are defined in the .env file and it is essential you create this file before running the application.
```
FLASK_CONFIG='default'
DATABASE_URI='database connection to be used'
SECRET_KEY='random string used for generating token'
TEST_DB='database to be used for testing'
SERVER_NAME='server in which app is being tested: `localhost:5000` works.'
```
7. After creating the `.env`, Setup up your database following these steps: 
    * `python manage.py db init`
    * `python manage.py db migrate`
    * `python manage.py db upgrade`
    
## API Documentation
Nitly exposes its data via an Application Programming Interface (API), so developers can interact in a programmatic way with the application. This document is the official reference for that functionality.

### API Resource Endpoints

URL Prefix = `http://sample_domain/api/v1` where sample domain is the root URL of the server HOST.


| EndPoint                                 | Functionality                 | Public Access|
| -----------------------------------------|-----------------------------|:-------------:|
| **POST** `/register`            | Registers a new user              |    TRUE    |
| **GET** `/token`        | Returns a Token  |    FALSE      |
| **GET** `/token/<token>/validity`           | Checks the validity of a token  |    TRUE    |
| **GET** `/<username>/<int:user_id>/token/refresh/`         | Refreshes a token  |    FALSE     |
| **POST** `/url/shorten/         `            | Returns a shortened url  | FALSE      |
| **GET** `/urls/`       | Returns list of all long urls       |    FALSE (admin only)     |
| **GET** `/shorten-urls/`        | Returns a list of all shortened urls      |    FALSE (admin only)    |
| **GET** `/shorten-urls/popularity/`             | Returns a list of all shortened urls ordered by their popularity |  FALSE   |
| **GET** `/user/urls/`                     | Returns a list of all long urls belonging to a particular user              |    FALSE     |
| **GET** `/user/shorten-urls/`                 | Returns a list of all shortened urls belonging to a particular user               |    FALSE     |
| **GET** `/user/shorten-urls/total/`                  | Returns the total shortened urls  belonging to a particular user          |    FALSE     |
| **GET** `/user/urls/total/` | Returns the total long url belonging to a particular user|   FALSE |
| **GET** `/shorten-url/<int:id>/url/`      | Returns the target url of the id specified shortened url       |    FALSE     |
| **GET** `/shorten-url/<shorten_url_name>/url/`    | Returns the  target url of the name specified shortened url   |    FALSE     |
| **PUT** `/shorten-urls/<int:id>/url/update/` | Updates the target url of a shortened url |    FALSE     |
| **PUT** `/shorten-urls/<int:id>/activate/` | Activates a deactivated shortened url |    FALSE     |
| **PUT** `/shorten-urls/<int:id>/deactivate/` | Deactivates an active shortened url|    FALSE     |
| **GET** `/user/profile` | Returns the profile of a user |    FALSE     |
| **DELETE** `/shorten-urls/<int:id>/delete/` | Deletes a shortened url |    FALSE     |
| **PUT** `/shorten-urls/<int:id>/restore/` | Restores a deleted shortened url |    FALSE     |

### <a name="usage"></a>Usage

1. To create a new user on the api:
    Input:
    ```cmd
    curl -i -X POST -H "Content-Type: application/json" -d '{"username": "user", "first_name":"micheal", "last_name":"power", "email":"noreply@andela.com", "password":"hello", "confirm_password":"hello"}' http://localhost:5000/api/v1.0/register
    ```
    Output:
    ```cmd
    {
      "message": "Successfully Registered"
    }
    ```


2. To get token:
    Input:
    ```cmd
    url -u "Content-Type: application/json" -d '{"username": "user", "password":"pwsd"}' http://localhost:5000/api/v1.0/token
    ```
    Output:
    ```
    {
      "expiration time": "Wed, 26 Apr 2017 09:16:10 AM",
      "expiration time in seconds": 1493194570,
      "message": "Authentication successful",
      "time generated": "Wed, 26 Apr 2017 08:16:10 AM ",
      "time generated in seconds": 1493190970,
      "token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ5MzE5NDU3MCwiaWF0IjoxNDkzMTkwOTcwfQ.eyJpZCI6MX0.WNgqUeHjLxkzZtVOvuJmrG_OZts_iav5Q2Ogxz5VZR0"
    }
    ```
    **NOTE:** The token needs to be attached to subsequent calls in order to access restricted resources.

3. Shorten a long URL:
    Input:
    ```
    curl -i -X POST -H '{"Authorization: Token eyJhbGciOiJIUzI1NiIsImlhdCI6MTQ5MzExMDQzMCwiZXhwIjoxNDkzMTE0MDMwfQ.eyJ1c2VyX2lkIjozfQ.NvL9u4eAO4iKB8pT501mk-BXx4Kq3p9gcTU83s23Nwo", "Content-Type: application/json"}' -d '{"long_url":"http://www.andela.com"}' http://localhost:5000/api/v1.0/url/shorten/
    ```
    Output:
    ```
    {
      "message": "Url successful shoretened",
      "shorten_url": {
        "id": 33,
        "shorten_url_name": "http://localhost:5000/ScCkep"
      }
    }
    ```

4. Get a list of user's shortened URLs:
    Input:
    ```cmd
    curl -i -X GET -H '{"Authorization: Token eyJhbGciOiJIUzI1NiIsImlhdCI6MTQ5MzExMDQzMCwiZXhwIjoxNDkzMTE0MDMwfQ.eyJ1c2VyX2lkIjozfQ.NvL9u4eAO4iKB8pT501mk-BXx4Kq3p9gcTU83s23Nwo", "Content-Type: application/json"}' http://localhost:5000/api/v1.0/user/shorten-urls
    ```
    Output:
    ```
    {
          "shorten_url_list": [
        {
          "date_added": "Tue, 11 Apr 2017 00:56:50 GMT",
          "deleted": false,
          "id": 1,
          "is_active": true,
          "long_url": "http://www.totallydifferenturl.com",
          "shorten_url_name": "http://localhost:5000/b1xz9A"
        },
        {
          "date_added": "Tue, 18 Apr 2017 03:48:25 GMT",
          "deleted": false,
          "id": 2,
          "is_active": true,
          "long_url": "http://www.google.com",
          "shorten_url_name": "http://localhost:5000/1aX3d0"
        },
        {
          "date_added": "Tue, 18 Apr 2017 03:48:25 GMT",
          "deleted": false,
          "id": 3,
          "is_active": true,
          "long_url": "http://www.facebook.com",
          "shorten_url_name": "http://localhost:5000/face"
        },
        {
          "date_added": "Fri, 21 Apr 2017 11:00:08 GMT",
          "deleted": false,
          "id": 5,
          "is_active": true,
          "long_url": "https://mail.google.com/mail/u/0/?tab=wm#inbox",
          "shorten_url_name": "http://localhost:5000/mailbox"
        }
    }
    ```

5. Deactivate a Shorten url:
    Input:
    ```cmd
    curl -i -X PUT -H '{"Authorization: Token eyJhbGciOiJIUzI1NiIsImlhdCI6MTQ5MzExMDQzMCwiZXhwIjoxNDkzMTE0MDMwfQ.eyJ1c2VyX2lkIjozfQ.NvL9u4eAO4iKB8pT501mk-BXx4Kq3p9gcTU83s23Nwo", "Content-Type: application/json"}' localhost:5000/api/v1.0/shorten-urls/1/deactivate/
    ```
    Output:
    ```
    {
      "message": "Successfully deactivated"
    }
    ```

6. Delete a shortened URL:
    Input:
    ```cmd
    curl -i -X DELETE -H '{"Authorization: Token eyJhbGciOiJIUzI1NiIsImlhdCI6MTQ5MzExMDQzMCwiZXhwIjoxNDkzMTE0MDMwfQ.eyJ1c2VyX2lkIjozfQ.NvL9u4eAO4iKB8pT501mk-BXx4Kq3p9gcTU83s23Nwo", "Content-Type: application/json"}' localhost:5000/api/v1.0/shorten-urls/1/delete/
    ```
    Output:
    ```
    {
      "message": "Successfully deleted"
    }
    ```

7. Get user profile
    Input:
    ```cmd
    curl -i -X GET -H '{"Authorization: Token eyJhbGciOiJIUzI1NiIsImlhdCI6MTQ5MzExMDQzMCwiZXhwIjoxNDkzMTE0MDMwfQ.eyJ1c2VyX2lkIjozfQ.NvL9u4eAO4iKB8pT501mk-BXx4Kq3p9gcTU83s23Nwo", "Content-Type: application/json"}' localhost:5000/api/v1.0/user/profile
    ```
    ```
    Output:
    ```
    {
      "date_added": "Sun, 08 Jan 2017 07:58:18 GMT",
      "email": "mich@yahoo.com",
      "firstname": "micheal",
      "id": 1,
      "lastname": "gab",
      "username": "user"
    }
    ```
 ### Running Tests
1. Navigate to the project directory.
2. Run `python manage.py test` to run test and check coverage.

## Authors

**Koya Gabriel.** - Software Developer at Andela

## Acknowledgments

Thanks to my facilitator **Njira Perci** and my wonderful **Pygo Teammates**