# project/server/config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'base'
    REDIS_URL = "redis://redis:6379/0"
    QUEUES = ["default"]


class ProductionConfig(Config):
    SECRET_KEY = 'prod'


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'dev'


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'test'
