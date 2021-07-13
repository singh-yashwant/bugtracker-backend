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
        # if the keys are missing
        if "title" not in data.keys():
            self.result["data"] = "insufficient details, title missing"
            return self.result, 400
        if "description" not in data.keys():
            self.result["data"] = "insufficient details, descritption missing"
            return self.result, 400
        if "priority" not in data.keys():
            self.result["data"] = "insufficient details, priority detials missing"
            return self.result, 400
        if "assignee" not in data.keys():
            self.result["data"] = "insufficient details, assignee missing"
            return self.result, 400
        if "tags" not in data.keys():
            self.result["data"] = "insufficient details, tags missing"
            return self.result, 400

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
            "status": "pending",
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
        
        # assigning this issue by running reassign issue function
        self.reassign_issues(teamName)

        return self.result, 200
    
    def getIssue(self, index, teamName):
        return self.issue_collection.find_one({"index":  index, "team": teamName})

    def reassign_issues(self, teamName):
        print("REASSIGNING ISSUES FOR TEAM", teamName)
        user_issue_limit = 100
        #1 fetch all the issues of the team
        #2 if an issue status is 'finished' free the assignee of that issue
        # and remove that issue from current list for further processing
        unfinished_issues = []
        for issue in self.issue_collection.find({"team": teamName}):
            if "status" not in issue.keys():
                issue["status"] = "pending"
                self.issue_collection.save(issue)
            if issue["status"] == "pending" and issue["assignee"] == "":
                unfinished_issues.append(issue)
        print("unfinished issues: ", unfinished_issues)

        #3 gather the list of team members who are working on less than the capped
        # count for each and sort the list using no of issues working on as key
        #4 remove the issues which are 'pending' and have a assignee assigned
        free_team_members = []
        for member in self.user_collection.find({"team": teamName}):
            if "issue-working" not in member.keys():
                member["issue-working"] = 0
                self.user_collection.save(member)
            if member["issue-working"] < user_issue_limit:
                free_team_members.append(member)
        free_team_members = sorted(free_team_members, key=lambda k: k["issue-working"])
        print("available team members", free_team_members)

        #5 while both issue list and member list both are non empty
        # assign the first issue to first team member and repeat from step 4
        while len(unfinished_issues) > 0 and len(free_team_members) > 0:
            print("\n\n**********start***************")
            print(unfinished_issues)
            print(free_team_members)
            print("**************end***********\n\n")
            cur_issue = unfinished_issues[0]
            cur_member = free_team_members[0]
            cur_issue["assignee"] = free_team_members[0]["name"]
            cur_member["issue-working"] += 1
            print("\n\nUPDATING ISSUE COUNT OF ", cur_member["name"], "\n")
            self.issue_collection.save(cur_issue)
            self.user_collection.save(cur_member)

            unfinished_issues = []
            free_team_members = []
            for member in self.user_collection.find({"team": teamName}):
                if member["issue-working"] < user_issue_limit:
                    free_team_members.append(member)
            
            for issue in self.issue_collection.find({"team": teamName}):
                if issue["assignee"] == "":
                    unfinished_issues.append(issue)
            free_team_members = sorted(free_team_members, key=lambda k: k["issue-working"])

        print("ISSUE REASSIGN COMPLETED")
       

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

        # reassigning all issues if current issue is finished
        if issueDetails["status"] == "finished":
            assignee = self.user_collection.find_one({"team": teamName, "name": issueDetails["assignee"]})
            assignee["issue-working"] -= 1
            print("decreasing issue-working count of ", assignee["name"])
            self.user_collection.save(assignee)
            self.reassign_issues(teamName)

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