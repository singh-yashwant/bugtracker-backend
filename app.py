import flask
from flask import request
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId 
from flask import jsonify, request


app = flask.Flask(__name__)

client = MongoClient("mongodb+srv://yashwant:yashwant@cluster0.jibtk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.get_database("bugtracker_db")

@app.route('/', methods=['GET'])
def home():
    return "api working"

# add a new user
@app.route('/add-user', methods=['POST'])
def add_user():
    _json = request.json
    _name = _json['name']
    _email = _json['email']

    if _name and _email and request.method == 'POST':
        db.users.insert({'name': _name, 'email': _email})

        resp = jsonify("User added successfully")
        resp.status_code = 200
        return resp
    
    else:
        return not_found()

@app.route('/users', methods=['GET'])
def users():
    users = db.users.find()
    resp = dumps(users)
    return resp

@app.route('/user/<id>', methods=['GET'])
def user(id):
    user = db.users.find_one({"_id":ObjectId(id)})
    resp = dumps(user)
    return resp

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': "not found" + request.url
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

app.run(debug=True)