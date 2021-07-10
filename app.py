from flask import Flask
from flask_restful import Api
from flask_cors import CORS 

from models.home import Home
from models.registerTeam import RegisterTeam
from models.issues import CreateIssue
from models.issues import UpdateIssue
from models.issues import IssueList
from models.user import UserList
from models.auth import Autharization
from models.auth import LogIn
from models.test import TestClass
from models.auth import IsTokenValid
from models.dashboard import Dashboard
from models.issues import ReassignIssues

app = Flask(__name__)
api = Api(app)
CORS(app)

app.config['SECRET_KEY'] = Autharization().generateSecretKey()

api.add_resource(Home, '/')
api.add_resource(RegisterTeam, '/register-team')
api.add_resource(CreateIssue, '/create-issue')
api.add_resource(UpdateIssue, '/update-issue')
api.add_resource(IssueList, '/issues')
api.add_resource(UserList, '/users')
api.add_resource(LogIn, '/login')
api.add_resource(TestClass, '/test')
api.add_resource(IsTokenValid, '/check-token')
api.add_resource(Dashboard, '/dashboard')

# temp code
rs = ReassignIssues()
rs.update_issues(teamName='commando')

if __name__ == '__main__':
    app.run()
