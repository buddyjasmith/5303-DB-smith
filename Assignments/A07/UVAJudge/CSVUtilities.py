import csv
from http.client import responses
import json
import urllib
import urllib.request
import requests
import json
from pymongo import MongoClient
import gridfs
import io
from bson.objectid import ObjectId
from pprint import pprint
class CSVUtil:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = None
        self.collection = None
    
    def start_new_class(self, google_document_id, file_name, semester):
        print(f'File_name is {file_name}')
        # https://docs.google.com/spreadsheets/d/1jAkhTTA8b8BxF5ckkyct44jOz8PNmREB9QxGERVDSeY/edit#gid=0
        #! Represents the path to download spreadsheet to CSV files from google
        #! docs, this tends to break in the future.   
        google_doc_path = f'https://docs.google.com/spreadsheets/d/{google_document_id}/gviz/tq?tqx=out:csv&sheet=Sheet1'
        
        # Collect downloaded file from url and open as list of dicts
        response = urllib.request.urlopen(google_doc_path)
        json_array= []

        # read the csv as a list of dicts to aid in reading
        with io.TextIOWrapper(response, encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                item ={}
                for k,v in row.items():
                    if ((k == "Online Judge Username") and (v != '')):
                        item["UserName"] = v
                    elif (k == "Online Judge ID" and (v != '')):
                        item['JudgeID'] = int(v)
                    elif (k == "First" and (v != '')):
                        item['First'] = v
                    elif (k == 'Last' and (v != '')):
                        item['Last']= v
                    elif (k == "Link to Github Repo" and (v != '')):
                        item['Github'] = v
                if(item):
                    # if item contains key value pair, append to json array
                    item['solved'] = {}
                    json_array.append(item)
        if(json_array):
            # create file name to store json file 
            file_path = f'{file_name}.json'
            self.db = self.client[semester]
            self.collection = self.db[file_name]
            with open(file_path, 'w+') as jsonFile:
                jsonFile.write(json.dumps(json_array, indent=4))   
            self.collection.insert_many(json_array)
            # cursor = list(self.collection.find({},{'_id':0}))
            return {'STATUS': "OK"}
        else:
            return {"STATUS": "FAILED"}
        
        
    def get_class(self, class_name):
        self.collection = self.db[class_name]
        print(self.collection)
        cursor = list(self.collection.find({},{"_id":0}))
        print(cursor)
        return cursor

    def get_all_classes(self):
        collection_list = []
        collections = self.db.list_collection_names()
        for collection in collections:
            self.collection = self.db[collection]
            cursor = list(self.collection.find({},{"_id":0}))
            collection_list.append(cursor)    
        return collection_list    
    
    def check_entire_class(self, class_name, problem_list):
        #! NOT EVEN CLOSE....COME BACK FINISH ME!!!!!!!!!!!!!!
        self.collection = self.db[class_name]
        class_list = list(self.collection.find({},{"_id":0}))
        id_list = []
        for student in class_list:
            id_list.append(str(student["JudgeID"]))
        id_list=",".join(id_list)
        problem_list = ','.join(problem_list)
        print(type(id_list))
        uva_url = f'https://uhunt.onlinejudge.org/api/subs-pids/{id_list}/{problem_list}/0'
        results = requests.get(uva_url)
        results = json.loads(results.content)
        for k, v in results.items():
            print(f'{k} : {v}')
    def add_problem_to_list(self,collection, problems):
        self.collection = self.db[collection]
        result = self.collection.insert_many(problems)
        print(result)
    def download_problem_pdf(self, problem_id):
        set_number = str(problem_id)[:2]
        file_name = f'{problem_id}.pdf'

        url = f'https://onlinejudge.org/external/{set_number}/{file_name}'
        response = requests.get(url)

        self.db = self.client['problem_pdfs']
        self.collection = self.db[str(set_number)]
        fs = gridfs.GridFS(self.db)
        id = fs.put(response.content, filename=file_name, content_type='application/pdf')
        if_data = fs.exists({"filename":file_name})
        return if_data
    
    def get_pdf_by_number(self, problem_id):
        set_number = str(problem_id)[:2] if(len(str(problem_id)) > 3) else str(problem_id)[0]        
        file_name = f'{problem_id}.pdf'
        self.db = self.client['problem_pdfs']
        self.collection = self.db[str(set_number)]
        fs = gridfs.GridFS(self.db)
        pdf_exists = fs.exists({"filename":file_name})
        if (pdf_exists):
            file = fs.find({"filename":file_name})
            pdf_string = b''
            for item in file:
                pdf_string += item.read()
            # pdf_string = pdf_string.decode('utf-8')
            
            return pdf_string
        else:
            return []
    def update_class_submissions(self, db, collection):
        #! Update entire classes submissions
        #! Set Database and colleciton, semester/class
        self.db = self.client[db]
        self.collection = self.db[collection]
        class_list = list(self.collection.find())
        for student in class_list:
            self.update_student_submissions(student)
    def update_student_submissions(self, student):
        #! update individual student submissions
        problem_list = [
            'submissionID',
            'problemID',
            'verdictID',
            'runtime',
            'submissionTime',
            'languageId',
            'submissionRank'
            ]
        temp_list = []
        url = f'https://uhunt.onlinejudge.org/api/subs-user/{student["JudgeID"]}'
        result = requests.get(url)
        result = json.loads(result.content.decode())
        
        for item in result['subs']:
            #! merge problem_list and each submitted item data
            temp_item = dict(zip(problem_list,item ))
            temp_item['percentage'] = (temp_item['verdictID'] + 10) / 100.00 if temp_item['verdictID'] > 0 else 0
            #! make dict {problem_id : temp_item}
            pid = str(temp_item['problemID'])
            # temp_item = {pid: temp_item}
            #print(student['solved'])
            if( not pid in student['solved']):
                student['solved'][pid] = temp_item
                # pprint( student['solved'][pid])
            else:
                old_value = student['solved'][pid]['verdictID']
                new_value =temp_item['verdictID']
                if(old_value < new_value):
                    student['solved'][pid]=temp_item
        
        self.collection.update_one({"_id":student["_id"]},{"$set":{"solved":student['solved']}})
        #self.collection.replace_one({"_id": student["id"]},{})
        

    def update_user_submissions(self, uid, db, collection):
        self.db = self.client[db]
        self.collection = self.db[collection]
        cursor = list(self.collection.find({"JudgeID": uid}))
        print(cursor)
        problem_list = [
            'submissionID',
            'problemID',
            'verdictID',
            'runtime',
            'submissionTime',
            'languageId',
            'submissionRank'
            ]
        temp_list = []
        url = f'https://uhunt.onlinejudge.org/api/subs-user/{uid}'
        result = requests.get(url)
        result = json.loads(result.content.decode())
        for item in result['subs']:
            temp_list.append( dict(zip(problem_list,item )))
        for item in cursor:
            item['solved']= temp_list
        self.collection.update_one({"_id":cursor["_id"]},{"$set":{"solved":temp_list}})
    def get_user_stats(self, uid, database, collection):
        self.db = self.client[database]
        self.collection = self.db[collection]
        cursor = list(self.collection.find({"JudgeID": uid},{"_id":0}))
        
        print(cursor)

if __name__ == '__main__':
    csvutil = CSVUtil()
    #csvutil.update_class_submissions('fall_21','4883_fall_21')
    csvutil.start_new_class("1jAkhTTA8b8BxF5ckkyct44jOz8PNmREB9QxGERVDSeY", '4883_fall_21', 'fall_21')
    csvutil.update_class_submissions('fall_21','4883_fall_21')
    #csvutil.check_entire_class("4883_fall_21",["161"])
    #csvutil.add_problem_to_list("fall_21_problems",[{"Title":"test", "Problem_Number": 25}])
    #csvutil.download_problem_pdf(1579)
    
    #csvutil.check_user_submissions(845581,'fall_21', '4883_fall_21')
    #csvutil.get_user_stats(845581,'fall_21', '4883_fall_21')

    #csvutil.check_user_submissions(845581, 'fall_21','4883_fall_21' )