import csv
from http.client import responses
import json
from copy import deepcopy
import urllib
import urllib.request
import requests
import json
from pymongo import MongoClient
import gridfs
import io
import datetime
import pytz
from models import PdfModel
from bson.objectid import ObjectId
from pprint import pprint
import time
class UVAUtil:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = None
        self.collection = None
        self.grade_percentage = {
            10 : .25,
            15 : .25,
            20 : 0,
            30 : .0,
            35 : .3,
            40 : .3,
            45 : .5,
            50 : .5,
            60 : .5,
            70 : .5,
            80 : .75,
            90 : 1
        }
    
    def start_new_class(self, google_document_id, class_name):
        print(google_document_id)
        print(class_name)
        # https://docs.google.com/spreadsheets/d/1jAkhTTA8b8BxF5ckkyct44jOz8PNmREB9QxGERVDSeY/edit#gid=0
        #! Represents the path to download spreadsheet to CSV files from google
        #! docs, this tends to break in the future.   
        google_doc_path = f'https://docs.google.com/spreadsheets/d/{google_document_id}/gviz/tq?tqx=out:csv&sheet=Sheet1'
        
        # Collect downloaded file from url and open as list of dicts
        try:
            response = urllib.request.urlopen(google_doc_path)
            json_array= []
        except urllib.error.HTTPError as e:
            print('Invalid class id passed')
            return {
                "Status": "Failed",
                "Message": e,
                
            }

        # read the csv as a list of dicts to aid in reading
        with io.TextIOWrapper(response, encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                item ={}
                for k,v in row.items():
                    if ((k == "online Judge Username") and (v != '')):
                        item["userName"] = v
                    elif (k == "Online Judge ID" and (v != '')):
                        item['judgeID'] = int(v)
                    elif (k == "First" and (v != '')):
                        item['first'] = v
                    elif (k == 'Last' and (v != '')):
                        item['last']= v
                    elif (k == "Link to Github Repo" and (v != '')):
                        item['github'] = v
                if(item):
                    # if item contains key value pair, append to json array
                    item['solved'] = {}
                    item['required_assns']= {}
                    json_array.append(item)
        if(json_array):
            # create file name to store json file 
            file_path = f'{class_name}.json'
            self.db = self.client['class']
            self.collection = self.db[class_name]
            with open(file_path, 'w+') as jsonFile:
                jsonFile.write(json.dumps(json_array, indent=4))   
            self.collection.insert_many(json_array)
            # cursor = list(self.collection.find({},{'_id':0}))
            return {'STATUS': "OK"}
        else:
            return {"STATUS": "FAILED"}

    def __get_assignments(self, class_name):
        self.db = self.client['assignments']
        self.collection = self.db[class_name]
        assignments = list(self.collection.find({},{"_id":0}))
        return assignments
    def __get_students_by_class(self,class_name):
        self.db = self.client['class']
        self.collection = self.db[class_name]
        students = list(self.collection.find())
        return students
    def grade_by_class(self, class_name):
        import time
        assignments = self.__get_assignments(class_name)
        students = self.__get_students_by_class(class_name)
        for student in students:
            self.grade_by_student(student, assignments)
        # for assignment in assignments:
        #     assn_num = assignment['assignment']
        #     for i in range(len(assignment['uva_num'])):
        #         num = assignment['uva_num'][i]
        #         percent = assignment['percentage'][i]
        #         required = int(assignment['required'])
        #         due_date = assignment['due_date']
                
        #         # num is uva_num in list 
        #         for student in students:
                    
        #             if str(num) in student['solved'] and required > 0: 
        #                 required = required - 1
        #                 penalty = 0.0
                        
        #                 sub_time = student['solved'][str(num)]['submissionTime']
        #                 if sub_time > due_date:
        #                     # print(f'penalty achieved for student {student["first"]} on {assn_num}')
        #                     penalty = .1
        #                 print(f'sub_time is {sub_time} due date is {due_date}')
        #                 if assn_num in student['required_assns']:
        #                     student['required_assns'][assn_num]["points"]\
        #                         .append( [(percent - (percent * penalty))]),
                            
                            
        #                     student['required_assns'][assn_num]['required_achieved'] + 1
        #                     student['required_assns'][assn_num]['submission_times']\
        #                         .append(sub_time)  
                            
                            
        #                 else:
        #                     # print(type(student['required_assns']))
        #                     student['required_assns'][assn_num]={
        #                                 "points" : [(percent - (percent * penalty))],
        #                                 "required_achieved": 1,
        #                                 "submission_times" : [sub_time]
        #                         }
        # for student in students:
        #     self.collection.update_one({"_id":student["_id"]},{"$set":{"required_assns":student['required_assns']}})               
                            
                           
                            # student['required_assns'][assn_num]["submission_times"] = [sub_time]
                        # print('***************************************')
                        # print(f'{student["first"]} {student["last"]}')              
                        # pprint(student['required_assns'])
                      
    def grade_by_student(self, student, assignments):
        import _testimportmultiple
        for assignment in assignments:
            penalty = 0.0
            req_solves = int(assignment['required'])
            uva_list = assignment['uva_num']
            weights = assignment['weights']
            num_pnts= dict(zip(assignment['uva_num'],assignment['percentage']))
            assignment_number = assignment['assignment']            
            due_time = time.mktime(assignment['due_date'].timetuple())
            # for problem in uva_list:
            for i in range(len(uva_list)):
                problem = uva_list[i]
                
                print(f'PROBLEM = {problem}')
                print(f'Len(uva_list) = {len(uva_list)}')
                if str(problem) in student['solved']:
                    try:
                        sub_time = time.mktime(student['solved'][str(problem)]['submissionTime'].timetuple())
                    except Exception as e:
                        print(f'Error: {e}')
                        pprint(student)
                    print(f'Problem: {problem} found in {student["first"]}s data')
                    penalty = .15 if sub_time > due_time  else 0.0
                  
                    if not assignment_number in student['required_assns'] and (req_solves > 0):
                        req_solves = req_solves - 1
                        student['required_assns'][assignment_number]={
                            "problem_number": [problem],
                            "on_time": [False if sub_time > due_time else True],
                            "due_time": [due_time],
                            "submitted": [sub_time],
                            "points" : [weights[i] * (num_pnts[problem] - (num_pnts[problem] * penalty))]
                        }
                    elif (req_solves > 0) and (assignment_number in student['required_assns']):
                        req_solves = req_solves - 1
                        try:
                            student['required_assns'][assignment_number]['problem_number']\
                                .append(problem)
                            student['required_assns'][assignment_number]['on_time']\
                                .append(False if sub_time > due_time else True)
                            student['required_assns'][assignment_number]['due_time']\
                                .append(due_time)
                            student['required_assns'][assignment_number]['submitted']\
                                .append(sub_time)
                            student['required_assns'][assignment_number]['points']\
                                .append(weights[i] * (num_pnts[problem] - (num_pnts[problem] * penalty)))
                        except Exception as e:
                            print(f'ERROR: {e}')
                            print(f'Problem {problem}')
                            print(f'The value of I is {i}')
                            print(len(weights), len(num_pnts))
                            time.sleep(3)
        self.collection.update_one({"_id":student["_id"]},{"$set":{"required_assns":student['required_assns']}})
        


    
    def get_class(self, class_name):
        self.db = self.client['class']
        self.collection = self.db[class_name]
        print(self.collection)
        cursor = list(self.collection.find({},{"_id":0}))
        return cursor

    def get_all_classes(self,):
        collection_list = []
        self.db = self.client['class']
        collections = self.db.list_collection_names()
        for collection in collections:
            self.collection = self.db[collection]
            cursor = list(self.collection.find({},{"_id":0}))
            temp_dict={}  
            temp_dict[collection] = cursor         
            collection_list.append(temp_dict)    
        return collection_list    
    def get_class_list(self):
        self.db = self.client['class']
        classes = self.db.list_collection_names()
        return classes
        
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
        set_number = str(problem_id)[:2] if(len(str(problem_id)) == 4) else str(problem_id)[:3] if (len(str(problem_id))==5) else str(problem_id)[0]      
        file_name = f'{problem_id}.pdf'

        url = f'https://onlinejudge.org/external/{set_number}/{file_name}'
        print(url)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.HTTPError as exception:
            print(exception)
            return exception
        self.db = self.client['problem_pdfs']
        self.collection = self.db[str(set_number)]
        fs = gridfs.GridFS(self.db)
        id = fs.put(response.content, filename=file_name, content_type='application/pdf')
        if_data = fs.exists({"filename":file_name})
        return if_data
    
    def get_pdf_by_number(self, problem_id):
        set_number = str(problem_id)[:2] if(len(str(problem_id)) == 4) else str(problem_id)[:3] if (len(str(problem_id))==5) else str(problem_id)[0]        
        file_name = f'{problem_id}.pdf'
        print(set_number)
        print(file_name)
        self.db = self.client['problem_pdfs']
        self.collection = self.db[str(set_number)]
        fs = gridfs.GridFS(self.db)
        pdf_exists = fs.exists({"filename":file_name})
        print(pdf_exists)
        if (pdf_exists):
            file = fs.find({"filename":file_name})
            pdf_string = b''
            for item in file:
                pdf_string += item.read()
            # pdf_string = pdf_string.decode('utf-8')
            
            return pdf_string
        else:
            return []
    def set_problem_list(self):
        self.db = self.client['id_lookup']
        self.collection = self.db['problems']
        url = 'https://uhunt.onlinejudge.org/api/p'
        response = requests.get(url)
        result = json.loads(response.content.decode())
        id_list = []
        for item in result:
            
            temp = {"problem_id" : item[0],"problem_num": item[1], "title": item[2]}
            self.collection.insert_one(temp)
        
       


    def update_class_submissions(self,  class_name):
        # get list of all assignment problems for class
        self.db = self.client['problem_lists']
        self.collection = self.db[class_name]
        #collect all assignment numbers, turn into one list
        problem_list = list(self.collection.find({},{"_id":0}))
        problem_nums = []
        for k, v in problem_list[0].items():
            for item in v:
                problem_nums.append(item)
        
        
        
        
 
        # reset database and collection to class['semester_year'] example
        self.db = self.client['class']
        self.collection = self.db[class_name]
        class_list = list(self.collection.find())
        
        result_list = []
        if(len(class_list) >0):
            # if shit exists
            for student in class_list:
                update_message = f'Beginning update operation on {student["first"]} {student["last"]}'
                print(update_message)
                result = self.update_student_submissions(student, problem_nums)
                result_list.append(result)    
        else:
            return f'Non-Existent collection: {class_name}'
        return result_list
        




    def update_student_submissions(self, student, problemnums):
        id_db = self.client['id_lookup']
        collection = id_db['problems']
        # result = list(collection.find({}))
        # print(result)
        
        problem_list = [
            'submissionID',
            'problemNum',
            'verdictID',
            'runtime',
            'submissionTime',
            'languageId',
            'submissionRank'
            ]
            
        id = student['judgeID']
        problemnums = [str(element) for element in problemnums]
        problemnums = ','.join(problemnums)
        
        url = f'https://uhunt.onlinejudge.org/api/subs-nums/'\
              f'{id}/{problemnums}/0'
        
        
        result = requests.get(url)
        result = json.loads(result.content.decode())
        for k, v in result.items():
            print('New key Value')
            print(k + ':')
            for key, value in v.items():
                if key == 'subs':
                    for item in value:
                        result = collection.find_one({'problem_id': item[1]},{'_id':0, 'problem_num': 1, 'title':1})
                        item[1] = result['problem_num']
                        
                        temp_dict= dict(zip(problem_list,item ))
                        temp_dict['title'] = result['title']
                        temp_dict['percentage'] =self.grade_percentage[temp_dict['verdictID']]
                        temp_dict['submissionTime'] = datetime.datetime.fromtimestamp(temp_dict['submissionTime'] )

                        p_num_exist_in_students = temp_dict['problemNum'] in student['solved'].keys()
                        if not p_num_exist_in_students:
                            student['solved'][str(temp_dict['problemNum'])] = temp_dict
                        elif p_num_exist_in_students:
                            new_grade = temp_dict['percentage'] 
                            old_grade = student['solved'][temp_dict['problemNum']]['percentage']
                            if new_grade > old_grade:
                                student['solved'][str(temp_dict['problemNum'])]['percentage'] = new_grade
        try:
            self.collection.update_one({"_id":student["_id"]},{"$set":{"solved":student['solved']}})
            name = student['first'] + student['last']
            return f'Sucessfully update student: {name}'
        except Exception as e:
            name = f'{student["first"]}  {student["last"]}'

            print(f'An exeption occurred while updating:  {name}: of type {e}')
            
            return f'An exeption occurred while updating: {name}'
        return
        for problem in result:
            num = list(collection.find({'problem_id"': problem[1]},{'problem_num':1}))
            print(num)
        return
        for k, v in result.items():
            for key, value in v.items():
                if key == 'subs':   
                    for item in value:
                        temp_dict = None
                        temp_dict= dict(zip(problem_list,item ))
                        pprint(temp_dict)
                        return
                        temp_dict['percentage'] =self.grade_percentage[temp_dict['verdictID']]
                        problem_number = str(temp_dict['problemNum'])
                        p_num_exist_in_students = problem_number in student['solved'].keys()
                        
                        if p_num_exist_in_students == False:
                            # problem number is not in solved add it to solved
                            print('shit doesnt exist, insert solved dict')
                            student['solved'][problem_number] = temp_dict
                        elif p_num_exist_in_students:
                            temp_percent = temp_dict['percentage']
                            stud_percent = student['solved'][problem_number]['percentage']
                            if temp_percent > stud_percent:
                                student['solved'] = temp_dict
        try:
            self.collection.update_one({"_id":student["_id"]},{"$set":{"solved":student['solved']}})
            name = student['first'] + student['last']
            return f'Sucessfully update student: {name}'
        except Exception as e:
            name = f'{student["first"]}  {student["last"]}'

            print(f'An exeption occurred while updating:  {name}: of type {e}')
            
            return f'An exeption occurred while updating: {name}'
        # pprint(student)
        
        

   

   
    def add_class_problem(self, db, collection, list_probs):
        self.db = self.client[db]
        self.collection = self.db[collection]
        problem_list = []
        us_cntrl = pytz.timezone('US/Central')
        for problem in list_probs:
            problem_list.extend(problem['uva_num'])
            
            self.collection.insert_one(problem)
        self.db = self.client['problem_lists']
        self.collection = self.db[collection]
        self.collection.insert_one({"problems": problem_list})
    def update_user_grades(self, db, collection):
        # set class and semester_year
        self.db = self.client[db]
        self.collection = self.db[collection]
        # get all files of semester_year 
        results = list( self.collection.find({}))

        # get list of assignments and percentages
        assn_db = self.client['assignments']
        assn_collection = assn_db[collection]
        assignments = list(assn_collection.find({}))
        uva_percentages = []
        for assignment in assignments:
            '''
            #Create dictionary of {uva_num: percentage_value} for each assn
            #append that to each assignment in assignments for easier access 
            #in grading 
            '''
            # uva_percentages[assignment['assignment']] = dict(zip(assignment['uva_num'], assignment['percentage']))
            # assignment['grade_criteria'] = uva_percentages[assignment['assignment']]
            id_list = assignment['uva_num']
            for i in range(0, len(id_list)):
                id_list[i] = int(id_list[i])
            uva_percentages.append( dict(zip(assignment['uva_num'], assignment['percentage'])))
            
            # assignment['grade_criteria'] = uva_percentages[assignment['assignment']]
        percent_dict ={}
        # for row in uva_percentages:
        #     for k,v in row.items():
        #         k = int(k)
        #         v= float(v)
        for row in uva_percentages:
            for k,v in row.items():
                print(k,v)
        # print(len(uva_percentages))
        # print(uva_percentages)
        for item in results:
            for k,v in item.items():
                
                if k == 'solved':
                    for key0, value0 in v.items():
                        id = int(value0['problemID'])
                        percentage = float(value0['percentage'])
                        print(f'{id}{type(id)} :: {percentage}{type(percentage)} ')
                        if percent_dict.get(int(id)) is not None:
                            print(f"Yes, key: '{id}' exists in dictionary ")
                        else:
                            print(f"No, key: '{id}' does not exists in dictionary {type(id)}")
    def compare_solved(self, db, collection, submitted):
        # pprint(submitted)
        self.db = self.client[db]
        self.collection = self.db[collection]
    
    def get_user_stats(self, uid, database, collection):
        self.db = self.client[database]
        self.collection = self.db[collection]
        cursor = list(self.collection.find({"JudgeID": uid},{"_id":0}))
        print(cursor)

if __name__ == '__main__':
    uvautil = UVAUtil()
    uvautil.start_new_class(
        "1jAkhTTA8b8BxF5ckkyct44jOz8PNmREB9QxGERVDSeY", 
        'Fall_2021'
        )
    # uvautil.set_problem_list()
    
    
    prob_list = [
        {"assignment":"A04",
        "title":["Hashmat the brave warrior"],
        "required":1,
        "uva_num":[10055],
        "percentage":[1.0],
        "due_date": datetime.datetime(2021,8,31,14,0,0),
        "completed": {},
        "weights":[100]
        },
        {"assignment":"A05",
        "title":["Traffic Lights"],
        "required": 1,
        "uva_num":[161],
        "percentage":[1.0],
        "due_date":datetime.datetime(2021, 9,7,23,59),
        "completed": {},
        "weights":[100]
        },
        {"assignment":"A06",
        "title":["Jolly Jumpers"],
        "required":1,
        "uva_num":[10038],
        "percentage":[1.0],
        "due_date": datetime.datetime(2021,9,9,15,20),
        "completed": {},
        "weights":[100]
        },
        {
            "assignment":"A07",
            "title":["Place the Guards"],
            "required":"1",
            "uva_num":[11080],
            "percentage":[1],
            "due_date": datetime.datetime(2021,9,14,15,20),
        "completed": {},
        "weights":[100]
        },
        {"assignment":"A08",
        "title":["Hardwood Species","Football Problem"],
        "required":1,
        "uva_num":[10226,10194],
        "percentage":[.5, .5],
        "due_date": datetime.datetime(2021,9,21,15,20),
        "completed": {},
        "weights":[50,50]
        },
        {"assignment":"A09",
        "title":["Never Ending Towers of Hanoi"],
        "required":1,
        "uva_num":[10017],
        "percentage":[1.0],
        "due_date": datetime.datetime(2021,9,28,15,20),
        "completed": {},
        "weights":[100]
        },
        {"assignment":"A10",
        "title":["Brick Wall Patterns"],
        "required":1,
        "uva_num":[900,920],
        "percentage":[.5, .5],
        "due_date": datetime.datetime(2021, 9, 30,15,20),
        "completed": {},
        "weights":[50,50]
        },
        {"assignment":"A11",
        "title":["Maximum Sum"],
        "required":1,
        "uva_num":[108],
        "percentage":[1],
        "due_date": datetime.datetime(2021, 10, 7,15,20),
        "completed": {},
        "weights":[100]
        },
        {"assignment":"A13",
        "title":["Mice and Maze"],
        "required":1,
        "uva_num":[1112],
        "percentage":[1.0],
        "due_date": datetime.datetime(2021, 10, 26, 15, 20),
        "completed": {},
        "weights":[100]
        },
        {"assignment":"A14",
        "title":["3n + 1", "TEX Quotes", "Skew Binary", "Primary Arithmetic",
                "Hashmat the brave Warrior","Back to Highschool Physics",
                "Summation of Polynomials","Peters Smokes","Above Average",
                "Back to Intermediate Math", "Odd Sum", 
                "Parity","Searching for Nessy", "Relation Operator", 
                "Division of Nlogonia", "Automatic Answer","Etruscan Warriors",
                "Hello World","Cost Cutting","Jumping Mario","Automate the Grades",
                "Horror Dash","Bafana Bafana","Egypt","Brick Game","Language Detection",
                "One-Two-Three","Save Setu", "Hajj-e-akbar","10:6:2"],
        "required":3,
        "uva_num":[100,272,575,10035,10055,10071,10302,10346,10370,10773, 
                  10783,10931,11044,11172,11498,11547,11614,11636,11727,11764,
                  11777,11799,11805,11854,11875,12250,12289,12403,12577,12578],
        "percentage":[.3333,.3333,.3333,.3333,.3333,.3333,.3333,.3333,.3333,.3333,
                      .3333,.3333,.3333,.3333,.3333,.3333,.3333,.3333,.3333,.3333,
                      .3333,.3333,.3333,.3333,.3333,.3333,.3333,.3333,.3333,.3333],
        "due_date": datetime.datetime(2021, 11, 21,15,20),
        "completed": {},
        "weights":[33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,
                  33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,
                  33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3]
        },
        {"assignment":"A17",
        "title":["Tree Summing"],
        "required":1,
        "uva_num":[112],
        "percentage":[1],
        "due_date": datetime.datetime(2021, 11, 23,15,20),
        "completed": {},
        "weights":[100]
        },
    ]
    # *******************************************
    uvautil.add_class_problem('assignments','Fall_2021',prob_list)
    uvautil.update_class_submissions('Fall_2021')
    uvautil.grade_by_class('Fall_2021')
   
   
    # print(uvautil.get_class_list())

    ###  start new class and update submissions
    # uvautil.start_new_class(
    #     "1jAkhTTA8b8BxF5ckkyct44jOz8PNmREB9QxGERVDSeY", 
    #     'Fall_2021'
    #     )
    

    #print(uvautil.get_pdf_by_number(10791))
    #print(uvautil.get_all_classes())

    #uvautil.update_user_grades('class', 'Fall_2021')
