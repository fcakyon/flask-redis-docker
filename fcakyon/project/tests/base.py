# project/tests/base.py


from project.server import create_app
import unittest

app = create_app()


class BaseTestCase(unittest.TestCase):
    client = app.test_client()
    
    def create_app(self):
        app.config.from_object("project.server.config.TestingConfig")
        return app

    def setUp(self):
        pass

    def tearDown(self):
        pass
