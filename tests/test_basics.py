# coding=utf-8
import unittest

from flask import current_app

from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exist(self):
        """tests whether a false return is gotten for a non existing app"""
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """
        tests the configuration setup if it returns true if an application is
        created
        """
        self.assertTrue(current_app.config["TESTING"])
