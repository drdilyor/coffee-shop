from flask import Flask, request, jsonify, abort
from sqlalchemy.exc import SQLAlchemyError
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink  # noqa
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    return {
        'success': True,
        'drinks': [d.short() for d in Drink.query.all()]
    }


'''
DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    return {
        'success': True,
        'drinks': [d.long() for d in Drink.query.all()]
    }


'''
DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    data = request.get_json() or abort(400)
    title = data.get('title') or abort(400)
    recipe = data.get('recipe') or abort(400)
    recipe = json.dumps(recipe)

    drink = Drink(title=title, recipe=recipe)
    try:
        drink.insert()
    except SQLAlchemyError:
        abort(422)
    return {
        'success': True,
        'drinks': [drink.long()]
    }


'''
DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(_payload, id: int):
    drink: Drink = Drink.query.get(id) or abort(404)
    data = request.get_json()

    if 'title' in data:
        drink.title = data['title']
    if 'recipe' in data:
        drink.recipe = json.dumps(data['recipe'])
    try:
        drink.update()
    except SQLAlchemyError:
        abort(422)

    return {
        'success': True,
        'drinks': [drink.long()]
    }


'''
DONE implement endpoint
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
def delete_drink(_payload, id: int):
    drink: Drink = Drink.query.get(id) or abort(404)
    try:
        drink.delete()
    except SQLAlchemyError:
        abort(422)
    return {
        'success': True,
        'delete': id
    }



## Error Handling
'''
DONE implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(_e):
    return {
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }, 404


@app.errorhandler(400)
def bad_request(_e):
    return {
        'success': False,
        'error': 400,
        'message': 'bad request'
    }, 400


@app.errorhandler(403)
def forbidden(_e):
    return {
        'success': False,
        'error': 403,
        'message': 'forbidden'
    }, 403


@app.errorhandler(422)
def unprocessable(_e):
    return {
        'success': False,
        'error': 422,
        'message': 'unprocessable'
    }, 422


'''
DONE implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def not_found(e: AuthError):
    from sys import exc_info
    print(exc_info())
    return {
        'success': False,
        'error': e.status_code,
        'message': e.error,
    }, e.status_code
