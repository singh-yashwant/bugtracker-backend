from pymongo import MongoClient
from config import MONGO_CONNECTION_URL
from bson.objectid import ObjectId
from flask_restful import Resource
from flask import request
import json
from registerTeam import RegisterTeam
from auth import Autharization

# class to test the working of JWT based authorization
class TestClass(Resource):
    def __init__(self):
        self.client = MongoClient(MONGO_CONNECTION_URL)
        self.db = self.client.bugtracker_db
        self.user_collection = self.db.users
        self.team_collection = self.db.teams
        self.issue_collection = self.db.issues
        self.result = {"Status": True, "data": {}}
        self.registerTeam = RegisterTeam()

    def get(self):
        
        userDetails = Autharization.validate_token(request)
        if not userDetails:
            self.result["message"] = "Invalid or missing token"
            return self.result, 400
        
        print("userDetails", userDetails)
        return self.result, 200