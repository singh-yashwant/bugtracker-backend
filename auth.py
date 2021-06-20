from pymongo import MongoClient
from config import MONGO_CONNECTION_URL
from bson.objectid import ObjectId
from flask_restful import Resource
from flask import request
import json
import jwt
import datetime
from flask import current_app
from functools import wraps

class Autharization:
    def __init__(self):
        pass

    @staticmethod
    def generateSecretKey():
        return 'ThisIsSecretKey'

    @staticmethod 
    def matchPassword(savedPassword, providePassword):
        return savedPassword == providePassword

    @staticmethod 
    def generateToken(userEmail, teamName):
        token = jwt.encode({
                    "email": userEmail, 
                    "team": teamName, 
                    "exp": datetime.datetime.utcnow()+datetime.timedelta(minutes=60),
                    }, current_app.config["SECRET_KEY"],algorithm="HS256")
        return token


    @staticmethod
    def validate_token(request):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers["x-access-token"]
        else:
            return token

        try:
            userData = jwt.decode(token, current_app.config["SECRET_KEY"],algorithms="HS256")
            return userData
        except Exception as e:
            print("unable to decode token", e)
            return token
        
        

class LogIn(Resource):
    def __init__(self):
        self.client = MongoClient(MONGO_CONNECTION_URL)
        self.db = self.client.bugtracker_db
        self.user_collection = self.db.users
        self.team_collection = self.db.teams
        self.result = {"Status": True, "data": {}}

    def post(self):
        reqData = json.loads(request.data) if request.data else {}
        userEmail = reqData["email"] if "email" in reqData.keys() else ""
        teamName = reqData["team"] if "team" in reqData.keys() else ""
        password = reqData["password"] if "password" in reqData.keys() else ""

        print(reqData)
        if not userEmail or not teamName or not password:
            self.result["message"] = "incomplete user details"
            return self.result, 400

        userDetails = self.user_collection.find_one({"email": userEmail, "team": teamName})

        # checking if certain user with thse email and team name exist
        if not userDetails:
            self.result["message"] = "No user with these credentials exist"
            return self.result, 400
        
        # checking if the team with this name exist
        teamDetails = self.team_collection.find_one({"team-name": teamName})
        print(teamDetails)
        if not teamDetails:
            self.result["message"] = "No such team is registered on the application"
            return self.result, 400

        # matching the passoword provided with the team password
        if not Autharization().matchPassword(teamDetails["password"], password):
            self.result["message"] = "Incorrect password"
            return self.result, 400
            
        # Generate the auth token with 60 minutes expiry
        token = Autharization.generateToken(userEmail, teamName)
        print(token, type(token))

        self.result["message"] = "login successfull"
        self.result["token"] = token
        return self.result, 200