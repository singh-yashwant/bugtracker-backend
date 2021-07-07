from flask_restful import Resource
from flask import request

class Home(Resource):
    def __init__(self):
        self.result = {"Status": True, "data": "api working"}
    def get(self):
        return self.result, 200