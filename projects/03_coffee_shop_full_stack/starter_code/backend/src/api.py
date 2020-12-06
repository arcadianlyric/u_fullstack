import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["GET"])
def get_drinks():
    results = {
        "success": True,
        "drinks": [drink.short() for drink in Drink.query.all()]
    }
    return jsonify(results)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_detail(jwt):
    results = {
        "success": True,
        "drinks": [drink.long() for drink in Drink.query.all()]
    }
    return jsonify(results)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drink(jwt):
    """Adds a drink. Requires authentication and permission"""
    body = request.get_json()
    if not body:
        abort(400)

    drink = Drink(title=body["title"], recipe=json.dumps(body["recipe"]))
    drink.insert()
    results = {
        "success": True,
        "drinks": [drink.long()]
    }
    return jsonify(results)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def patch_drinks(jwt, drink_id):   # jwt must be the 1st
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)

    body = request.get_json()

    if not body or ("title" not in body and "recipe" not in body):
        abort(400)

    if "title" in body:
        drink.title = body["title"]
    if "recipe" in body:
        drink.recipe = json.dumps(body["recipe"])
    drink.update()

    results = {
        "success": True,
        "drinks": [drink.long()]
    }
    return jsonify(results)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drinks(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)

    drink.delete()
    return jsonify({
        "success": True,
        "delete": drink_id
        })


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return (jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422
            )


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return (jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404,
            )


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(401)
def Unauthorized(error):
    return (jsonify({
                    "success": False,
                    "error": 401,
                    "message": "Unauthorized request"
                    }), 401,
            )


@app.errorhandler(400)
def bad_request(error):
    return (jsonify({
                    "success": False,
                    "error": 400,
                    "message": "Bad request"
                    }), 400,
            )


@app.errorhandler(403)
def unauthorized(error):
    return (
        jsonify({"success": False, "error": 403, "message": "forbidden"}),
        403,
            )


@app.errorhandler(500)
def Internal_Server_Error(error):
    return (jsonify({
                    "success": False,
                    "error": 500,
                    "message": "Internal Server Error"
                    }), 500,
            )
