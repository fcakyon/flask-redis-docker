# project/tests/test__config.py


import unittest

from flask import current_app

from project.server import create_app

app = create_app()


class TestDevelopmentConfig(unittest.TestCase):
    def create_app(self):
        app.config.from_object("project.server.config.DevelopmentConfig")
        return app

    def test_app_is_development(self):
        self.assertFalse(current_app.config["TESTING"])
        self.assertTrue(app.config["DEBUG"] is True)
        self.assertFalse(current_app is None)


class TestTestingConfig(unittest.TestCase):
    def create_app(self):
        app.config.from_object("project.server.config.TestingConfig")
        return app

    def test_app_is_testing(self):
        self.assertTrue(current_app.config["TESTING"])
        self.assertTrue(app.config["DEBUG"] is True)


if __name__ == "__main__":
    unittest.main()
