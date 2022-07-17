import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
@requires_auth('get:drinks')
def drinks():
    """
        A function that gets all the avialble drinks 
    """
    try:
        all_drinks = Drink.query.all()
        drinks = [drink.short() for drink in all_drinks]

        if drinks == None:
            abort(404)
        else:
            return jsonify(
                {
                    "success": True, 
                    "drinks": drinks
                }
            )
    except Exception as e:
        abort(400)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_details():
    """
        An endpoint to GET drink in detail.
    """
    try:
        all_drinks = Drink.query.all()
        drinks = [drink.long() for drink in all_drinks]

        if drinks == None:
            abort(404)
        else:
            return jsonify(
                {
                    "success": True, 
                    "drinks": drinks
                }
            )
    except Exception as e:
        abort(400)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks():
    """
        A function to create a new drink 
    """
    try:
        body = request.get_json()
        title = body.get("title", None)
        recipe = body.get("recipe", None)

        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()
        drink = new_drink.long()

        return jsonify({
                    'success': True,
                    "drinks": drink
                })
    except Exception as e:
        abort(400)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks(id):
    try:
        body = request.get_json()
        title = body.get("title", None)
        recipe = body.get("recipe", None)

        drink = Drink.query.get(id)

        if title:
            drink.title = title
        if recipe:
            drink.recipe = recipe

        drink.update()

        drink = drink.long()
        return jsonify(
                    {
                        "success": True, 
                        "drinks": drink
                    } 
                )
    except Exception as e:
        abort(400)

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

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def remove_drinks(id):
    try:

        drink = Drink.query.get(id)

        drink.delete()
        return jsonify(
                    {
                        "success": True, 
                       "delete": id
                    } 
                )
    except Exception as e:
        abort(400)


# Error Handling
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


@app.errorhandler(404)
def not_found(error):
    return jsonify({
                "success": False,
                "error": 404,
                "message": "resource not found"
            }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad request"
        }), 400

@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False, 
        "error": 405,
        "message": "Method not allowed"
        }), 405
