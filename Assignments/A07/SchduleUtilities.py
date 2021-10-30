import json
from pymongo import MongoClient
from pprint import pprint

class ScheduleUtilities:
   
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client.Schedule
        self.collection = None
    def set_collection(self, collection):
        self.collection = collection
    def get_by_subject(self, subject):
        ...
    def get_by_crn(self, CRN):
        ...
    def get_by_instructor(self, instructor):
        ...
    def get_by_bldg(self, building):
        ...
        
