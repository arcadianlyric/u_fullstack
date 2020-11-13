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

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["GET"])
@requires_auth("get:drink")
def get_drinks(jwt):
    try:
        results = {
            "success": True,
            "drinks": [drink.short() for drink in Drink.query.all()]
        }
        return jsonify(results)
    except:
        abort(400)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks_details")
def get_drinks_detail(jwt):
    try:
        results = {
            "success": True,
            "drinks": [drink.long() for drink in Drink.query.all()]
        }
        return jsonify(results)
    except:
        abort(400)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
app.route("/drinks", methods=["POST"])
@requires_auth("post:drink")
def post_drinks(jwt):
    body = request.get_json()
    if not body or not body["title"] or not body["recipe"]:
        abort(400)
    new_drink = Drink(title=body["title"], recipe=json.dumps(body["recipe"]))
    new_drink.insert()

    results = {
        "success": True,
        "drinks": [new_drink.long()]
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
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drink")
def patch_drinks(drink_id, jwt):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)

    body = request.get_json()
    if not body or not body["title"] or not body["recipe"]:
        abort(400)
    drink.title = body["title"]
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
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth("delete:drink")
def delete_drinks(drink_id, jwt):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)

    drink.delete()
    return jsonify({
        "success": True,
        "delete": drink_id
        })

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

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
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(401)
def Unauthorized(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "Unauthorized request"
                    }), 401

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "Bad request"
                    }), 400