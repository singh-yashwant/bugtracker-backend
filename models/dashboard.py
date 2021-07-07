from pymongo import MongoClient
from config import MONGO_CONNECTION_URL
from bson.objectid import ObjectId
from flask_restful import Resource
from flask import request
import json
from .auth import Autharization

"""

header or /dashboard
"x-access-token": token

body for /dashboard
{
    "data": {
        "team-name": "temp",
        "project-name": "project name",
        "issue-list": [
            {
                "index": {
                    "title": "fake-title",
                    "summary": "fake",
                    "tags": ["list", "of", "tags"],
                    "author": "author name",
                    "author-email": "elkjteljk@lej",
                    "assignee": "this can be empty",
                    "priority": 1,
                    "description": "issue desc",
                }
            }
        ],
        "team-members": [
            {
                "email": "user@email",
                "name": "user name",
                 "issue-count": int,
            }
        ],
    }
}

"""

class Dashboard(Resource):
    def __init__(self):
        self.client = MongoClient(MONGO_CONNECTION_URL)
        self.db = self.client.bugtracker_db
        self.user_collection = self.db.users
        self.team_collection = self.db.teams
        self.issue_collection = self.db.issues
        self.result = {"Status": True, "data": {}}

    def get(self):
        self.userDetails = Autharization.validate_token(request)
        if not self.userDetails:
            self.result["message"] = "Invalid or missing token"
            return self.result, 400

        teamName = self.userDetails["team"]

        self.result["data"]["team-name"] = self.userDetails["team"]
        self.result["data"]["project-name"] = ""
        self.result["data"]["issue-list"] = []
        self.result["data"]["team-members"] = []
    
        #build the issue list
        issues = self.issue_collection.find({"team-name": teamName})
        for issue in issues:
            self.result["data"]["issue-list"].append(self.prepreIssueToReturn(issue))

        # build the team-members list
        users = self.user_collection.find({"team": teamName})

        for user in users:
            self.result["data"]["team-members"].append(self.prepreUserToReturn(user))

        return self.result, 200

    def prepreIssueToReturn(self, issue):
        data = dict()
        required_keys = ["index", "title", "tags", "author", "author-email", "assignee", "priority", "description"]
        for key in issue.keys():
            if key in required_keys:
                data[key] = issue[key]
        return data

    def prepreUserToReturn(self, user):
        data = dict()
        required_keys = ["name", "email", "issue-count"]
        for key in user.keys():
            if key in required_keys:
                data[key] = user[key]
        return data