# project/server/__init__.py


import os
from flask import Flask
from server.main.views import main_blueprint # blueprint1
import traceback  # error traceback
from flask import Flask, request, jsonify
from werkzeug.exceptions import default_exceptions  # exception handling
from werkzeug.exceptions import HTTPException  # exception handling


def create_app():

    # instantiate the app
    app = Flask(__name__, instance_relative_config=False)

    # set config
    app.config.from_object("server.config.ProductionConfig")

    # register blueprints
    app.register_blueprint(main_blueprint)

    # better exception handling
    @app.errorhandler(Exception)
    def handle_error(e):
        # 400 for https error, 500 for internal error
        if isinstance(e, HTTPException):
            # status_code = e.code
            status_code = 400
        else:
            status_code = 500
        # prepare error message
        message = str(e)
        # stdout error traceback
        print(traceback.format_exc())
        # return response
        return jsonify(message=message, error_traceback=traceback.format_exc()), status_code

    for ex in default_exceptions:
        app.register_error_handler(ex, handle_error)

    return app
