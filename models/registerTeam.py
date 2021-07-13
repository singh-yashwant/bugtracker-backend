from pymongo import MongoClient
from config import MONGO_CONNECTION_URL
from bson.objectid import ObjectId
from flask_restful import Resource
from flask import request
import json

"""

register-team json pyload format
{"team-name": "...", "team-members": [[name1, email1], [name2, email2], ....] ,"password": "..."}

"""

class RegisterTeam(Resource):
    def __init__(self):
        self.client = MongoClient(MONGO_CONNECTION_URL)
        self.db = self.client.bugtracker_db
        self.user_collection = self.db.users
        self.team_collection = self.db.teams
        self.result = {"Status": True, "data": {}}

    def post(self):
        reqData = json.loads(request.data) if request.data else None
        
        # if the keys are missing
        if "team-name" not in reqData.keys():
            self.result["data"] = "insufficient details, team-name missing"
            return self.result, 400
        if "project-name" not in reqData.keys():
            self.result["data"] = "insufficient details, project-name missing"
            return self.result, 400
        if "team-members" not in reqData.keys():
            self.result["data"] = "insufficient details, team-members detials missing"
            return self.result, 400
        if "password" not in reqData.keys():
            self.result["data"] = "insufficient details, password missing"
            return self.result, 400
               
        teamName = reqData["team-name"]
        self.password = reqData["password"]

        # if team with same name already present
        if self.sameNameTeamExist(teamName):
            self.result["data"] = "Cannot register team with same name already exist"
            return self.result, 400

        print("creating team", teamName)
        print("team details", reqData)
        self.createTeam(reqData)
        
        # add users to database
        self.addTeamMembersToDb(reqData["team-members"], teamName)
        self.result["data"] = "Team added successfully"
        return self.result, 200

    def createTeam(self, teamDetails):
        self.team_collection.insert(teamDetails)
        print("team added successfully")
    
    def sameNameTeamExist(self, teamName):
        if self.getTeam(teamName):
            return True
        return False

    def getTeam(self, teamName):
        return self.team_collection.find_one({"team-name": teamName})

    def addTeamMembersToDb(self, members, teamName):
        for member in members:
            user = {
                "name": member[0], 
                "email": member[1], 
                "team": teamName,
                "issue-working": 0
            }
            self.user_collection.save(user)
            self.sendEmail(teamName, member)

    def getIssueIndex(self, teamName):
        teamDetails = self.getTeam(teamName)
        if "issues" in teamDetails.keys():
            return teamDetails["issues"]+1
        else:
            return 1

    def updateIssueCount(self, teamName):
        try:
            teamDetails = self.getTeam(teamName)
            if "issues" in teamDetails.keys():
                teamDetails["issues"] += 1
            else:
                teamDetails["issues"] = 1
            self.team_collection.save(teamDetails)
            return True
        except:
            return False

    def sendEmail(self, teamName, userDetails):
        print("Sending email to", userDetails)
        userName = userDetails[0]
        email = userDetails[1]
        
        msg = """Hello {0}
Your team has successfully registered on bugtracker app 
These are your login credentials
username: {1}
passoword: {2}
""".format(userName, teamName, self.password)
