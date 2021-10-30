import json
from pymongo import MongoClient
from pprint import pprint

class StudeUtilities:
   
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client.student
        self.collection = self.db.under_graduate
    def get_student(self, page_size=10, page_num=1):
        skips = page_size * (page_num -1)
        cursor = list(
            self.collection.find({},{"_id":0}).skip(skips).limit(page_size)
        )
        return cursor
    def get_student_info(self, first_name=None, last_name=None, m_number=None, gpa=None):
        query ={}
        if(first_name):
            query['first_name'] = first_name
        if(last_name):
            query['last_name'] = last_name
        if(m_number):
            query['m_number'] = m_number
        if(gpa):
            query['gpa'] = gpa
        return list(self.collection.find(query, {"_id": 0}))
    
if __name__ == '__main__':
    su = StudeUtilities()
    print(su.get_student_info(first_name="Lacey"))


    