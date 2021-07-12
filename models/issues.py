from pymongo import MongoClient
from config import MONGO_CONNECTION_URL
from bson.objectid import ObjectId
from flask_restful import Resource
from flask import request
import json
from .registerTeam import RegisterTeam
from .auth import Autharization

"""

header or /create-issue
"x-access-token": token

body for /create-issue
{
    "title": "....",
    "description": "....",
    "priority": "....",
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
        userDetails = Autharization.validate_token(request)
        if not userDetails:
            self.result["message"] = "Invalid or missing token"
            return self.result, 400


        data = json.loads(request.data) if request.data else None
        print("CREATE ISSUE DATA REQUEST WITH")
        print(data)

        teamName = userDetails["team"]
        authorEmail = userDetails["email"]
        authorName = self.user_collection.find_one({"team": teamName, "email": authorEmail})["name"]
        issueIndex = self.registerTeam.getIssueIndex(teamName)

        print("fetching issue list for team", teamName)
        print("creating issue with index", issueIndex)

        issueData = {
            "team": teamName,
            "author": authorName,
            "author-email": authorEmail,
            "index": issueIndex,
            "tags": data["tags"],
            "title": data["title"],
            "assignee": data["assignee"],
            "priority": data["priority"],
            "description": data["description"]
        }
        print("creating this issue", issueData)

        # add issue to issues collection
        self.issue_collection.save(issueData)

        # update the issues count in team collection
        if self.registerTeam.updateIssueCount(teamName):
            print("issue count updated in team collection")
        else:
            print("Falied to update issue count in team collection")

        self.result["data"] = "Issue raised successfully"
        self.result["index"] = issueIndex
        return self.result, 200
    
    def getIssue(self, index, teamName):
        return self.issue_collection.find_one({"index":  index, "team": teamName})


"""
header for /update-issue
"x-access-token": token

body for /update-issue
{
    "index": issueindex,
    .
    .
    rest all the fields you want to update
    .
    .
}
"""

class UpdateIssue(CreateIssue):
    def post(self):
        userDetails = Autharization.validate_token(request)
        if not userDetails:
            self.result["message"] = "Invalid or missing token"
            return self.result, 400

        reqData = json.loads(request.data) if request.data else None
        
        teamName = userDetails["team"]
        
        index = reqData["index"]
        
        issueDetails = self.getIssue(index, teamName)
        for key in reqData.keys():
            issueDetails[key] = reqData[key]
        self.issue_collection.save(issueDetails)
        
        self.result["data"] = "Details update sucessfully"
        print(issueDetails)
        return self.result, 200

"""
header of /issues 
"x-access-token": token

body of /issues
blank
"""

class IssueList(CreateIssue):
    def get(self):
        userDetails = Autharization.validate_token(request)
        if not userDetails:
            self.result["message"] = "Invalid or missing token"
            return self.result, 400
        
        teamName = userDetails["team"]
        print("fetching issues for team ", teamName)

        issues = self.issue_collection.find({"team": teamName})

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