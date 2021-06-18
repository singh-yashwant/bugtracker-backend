from pymongo import MongoClient
from config import MONGO_CONNECTION_URL
from bson.objectid import ObjectId
from flask_restful import Resource
from flask import request
import json
from registerTeam import RegisterTeam

"""
issue object json
{
    "team-name": "....",
    "title": "....",
    "description": "....",
    "priority": "....",
    "author": "....",
    "assignee": "....",
    "tags": [..., ..., ...],
}

"""

class CreateIssue(Resource):
    def __init__(self):
        self.client = MongoClient(MONGO_CONNECTION_URL)
        self.db = self.client.bugtracker_db
        self.user_collection = self.db.users
        self.team_collection = self.db.teams
        self.issue_collection = self.db.issues
        self.result = {"Status": True, "data": {}}
        self.registerTeam = RegisterTeam()

    def post(self):
        reqData = json.loads(request.data) if request.data else None
        
        # fetch index for issue
        index = self.registerTeam.getIssueIndex(reqData["team-name"])
        print("issue index: ", index)

        # add issue to issues collection
        reqData["index"] = index
        self.issue_collection.save(reqData)

        # update the issues count in team collection
        if self.registerTeam.updateIssueCount(reqData["team-name"]):
            print("issue count updated in team collection")
        else:
            print("Falied to update issue count in team collection")

        # print(reqData)
        self.result["data"] = "Issue raised successfully"
        self.result["index"] = index
        return self.result, 200
    
    def getIssue(self, index, teamName):
        return self.issue_collection.find_one({"index":  index, "team-name": teamName})


class UpdateIssue(CreateIssue):
    def post(self):
        reqData = json.loads(request.data) if request.data else None
        index = reqData["index"]
        teamName = reqData["team-name"]

        issueDetails = self.getIssue(index, teamName)
        for key in reqData.keys():
            issueDetails[key] = reqData[key]
        self.issue_collection.save(issueDetails)
        
        self.result["data"] = "Details update sucessfully"
        print(issueDetails)
        return self.result, 200

class IssueList(CreateIssue):
    def get(self):
        reqData = json.loads(request.data) if request.data else None

        teamName = reqData["team-name"]
        issues = self.issue_collection.find({"team-name": teamName})

        self.result["data"]["issues"] = []
        for issue in issues:
            self.result["data"]["issues"].append(self.prepreIssueToReturn(issue))

        return self.result, 200

    def prepreIssueToReturn(self, issue):
        data = dict()
        required_keys = ["title", "team-name", "author", "description", "assignee", "priority", "tags", "index"]
        for key in issue.keys():
            if key in required_keys:
                data[key] = issue[key]
        return data