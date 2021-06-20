from pymongo import MongoClient
from config import MONGO_CONNECTION_URL
from bson.objectid import ObjectId
from flask_restful import Resource
from flask import request
import json
from registerTeam import RegisterTeam
from auth import Autharization

class UserList(Resource):
    def __init__(self):
        self.client = MongoClient(MONGO_CONNECTION_URL)
        self.db = self.client.bugtracker_db
        self.user_collection = self.db.users
        self.team_collection = self.db.teams
        self.issue_collection = self.db.issues
        self.result = {"Status": True, "data": {}}

    def get(self):
        userDetails = Autharization.validate_token(request)
        if not userDetails:
            self.result["message"] = "Invalid or missing token"
            return self.result, 400
        
        teamName = userDetails["team"]
        
        users = self.user_collection.find({"team": teamName})

        self.result["data"]["users"] = []
        for user in users:
            self.result["data"]["users"].append(self.prepreUserToReturn(user))

        return self.result, 200

    def prepreUserToReturn(self, user):
        data = dict()
        required_keys = ["name", "team", "email", "tags", "issue-count", "issue-list"]
        for key in user.keys():
            if key in required_keys:
                data[key] = user[key]
        return data
