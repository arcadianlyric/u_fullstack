import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)

    # Error Handling
    @app.errorhandler(400)
    def bad_request(error):
        return (jsonify({
                        "success": False,
                        "error": 400,
                        "message": "Bad request"
                        }), 400,
                )

    @app.errorhandler(401)
    def Unauthorized(error):
        return (jsonify({
                        "success": False,
                        "error": 401,
                        "message": "Unauthorized request"
                        }), 401,
                )

    @app.errorhandler(403)
    def unauthorized(error):
        return (
            jsonify({"success": False, "error": 403, "message": "forbidden"}),
            403,
                )

    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({
                        "success": False,
                        "error": 404,
                        "message": "resource not found"
                        }), 404,
                )

    @app.errorhandler(422)
    def unprocessable(error):
        return (jsonify({
                        "success": False,
                        "error": 422,
                        "message": "unprocessable"
                        }), 422
                )

    @app.errorhandler(500)
    def Internal_Server_Error(error):
        return (jsonify({
                        "success": False,
                        "error": 500,
                        "message": "Internal Server Error"
                        }), 500,
                )

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
