from flask import Flask
from flask_restful import Api
from flask_cors import CORS 

from home import Home
from registerTeam import RegisterTeam
from issues import CreateIssue
from issues import UpdateIssue

app = Flask(__name__)
api = Api(app)
CORS(app)

api.add_resource(Home, '/')
api.add_resource(RegisterTeam, '/register-team')
api.add_resource(CreateIssue, '/create-issue')
api.add_resource(UpdateIssue, '/update-issue')

if __name__ == '__main__':
    app.run()


# import flask
# from flask import request
# from pymongo import MongoClient
# from bson.json_util import dumps
# from bson.objectid import ObjectId 
# from flask import jsonify, request
# from config import MONGO_CONNECTION_URL


# app = flask.Flask(__name__)

# client = MongoClient(MONGO_CONNECTION_URL)
# db = client.get_database("bugtracker_db")


# add a new user
# @app.route('/add-user', methods=['POST'])
# def add_user():
#     _json = request.json
#     _name = _json['name']
#     _email = _json['email']

#     if _name and _email and request.method == 'POST':
#         db.users.insert({'name': _name, 'email': _email})

#         resp = jsonify("User added successfully")
#         resp.status_code = 200
#         return resp
    
#     else:
#         return not_found()

# @app.route('/users', methods=['GET'])
# def users():
#     users = db.users.find()
#     resp = dumps(users)
#     return resp

# @app.route('/user/<id>', methods=['GET'])
# def user(id):
#     user = db.users.find_one({"_id":ObjectId(id)})
#     resp = dumps(user)
#     return resp

# @app.errorhandler(404)
# def not_found(error=None):
#     message = {
#         'status': 404,
#         'message': "not found" + request.url
#     }
#     resp = jsonify(message)
#     resp.status_code = 404
#     return resp

# APIs to implement
# -register team
#     -register team members
# -login to dashboard with team name and password
# -create an issue
#     -reval all issues (assign new ones if possible) 
# -fetch all issues
# -change status of issues
#     -reval all issues (assign new ones if possible)
# -get team details
# -get user details
# -get issue details