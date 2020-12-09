import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json
from .database.models import db_drop_and_create_all, setup_db, dish
from .auth.auth import AuthError, requires_auth


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    '''
    Get ingradients by dishes
    Get dishes by ingradients
    '''
    
    @app.route('/dishes', methods=['GET'])
    def get_dishes():
        results = {
        "success": True,
        "dishes": [dish.short() for dish in Dish.query.all()]
    }
    return jsonify(results)


    @app.route("/dishes-detail", methods=["GET"])
    @requires_auth("get:dishes-detail")
    def get_dishes_detail(jwt):
        results = {
            "success": True,
            "dishes": [dish.long() for dish in dish.query.all()]
        }
        return jsonify(results)


    @app.route("/dishes", methods=["POST"])
    @requires_auth("post:dishes")
    def post_dish(jwt):
        """Adds a dish. Requires authentication and permission"""
        body = request.get_json()
        if not body:
            abort(400)

        dish = Dish(name=body["name"], recipe=json.dumps(body["recipe"]))
        dish.insert()
        results = {
            "success": True,
            "dishes": [dish.long()]
        }
        return jsonify(results)


    @app.route("/dishes/<int:dish_id>", methods=["PATCH"])
    @requires_auth("patch:dishes")
    def patch_dishes(jwt, dish_id):   # jwt must be the 1st
        dish = dish.query.get(dish_id)
        if not dish:
            abort(404)

        body = request.get_json()

        if not body or ("name" not in body and "recipe" not in body):
            abort(400)

        if "name" in body:
            dish.name = body["name"]
        if "recipe" in body:
            dish.recipe = json.dumps(body["recipe"])
        dish.update()

        results = {
            "success": True,
            "dishes": [dish.long()]
        }
        return jsonify(results)


    @app.route("/dishes/<int:dish_id>", methods=["DELETE"])
    @requires_auth("delete:dishes")
    def delete_dishes(jwt, dish_id):
        dish = Dish.query.get(dish_id)
        if not dish:
            abort(404)

        dish.delete()
        return jsonify({
            "success": True,
            "delete": dish_id
            })    


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
