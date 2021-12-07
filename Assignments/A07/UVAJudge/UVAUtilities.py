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
from datetime import timezone
import pytz
from copy import deepcopy
from models import PdfModel
from bson.objectid import ObjectId
from pprint import pprint
import time
from operator import itemgetter
from models import Assignment
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
                    print(k)
                    if ((k == "Online Judge Username") and (v != '')):
                        item["userName"] = v
                    elif (k == "Online Judge ID" and (v != '')):
                        item['judgeID'] = int(v)
                    elif (k == "First" and (v != '')):
                        item['first'] = v
                    elif (k == 'Last' and (v != '')):
                        item['last']= v
                    elif (k == "Link to Github Repo" and (v != '')):
                        item['github'] = v
                    elif (k == "Slack      Username" and (v != '')):
                        item['slack_username'] = v
                    elif (k =="Github    Username" and (v != '')):
                        item['github_username'] = v
                    elif (k == "Link to Github Repo" and (v != '')):
                        item['github_link'] = v
                if(item):
                    # if item contains key value pair, append to json array
                    item['solved_problems'] = {}
                    item['solved_problem_numbers'] = []
                    item['failed_to_solve'] = []
                    
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
       
                      
    def grade_by_student(self, student, assignments):
        import _testimportmultiple
        for assignment in assignments:
           
            penalty = 0.0
            req_solves = int(assignment['required'])
            uva_list = assignment['uva_id']
            weight = assignment['weight']
            #num_pnts= dict(zip(assignment['uva_id'],assignment['percentage']))
            num_pnts= zip(assignment['uva_id'],assignment['percent'])
            num_pnts = sorted(num_pnts, key=lambda x : x[1], reverse=True)
            num_pnts = dict(num_pnts)
            
            assignment_number = assignment['assn_num']            
            due_time = time.mktime(assignment['due_date'].timetuple())
            # for problem in uva_list:
            for i in range(len(uva_list)):
                problem = uva_list[i]
                
                # print(f'PROBLEM = {problem}')
                # print(f'Len(uva_list) = {len(uva_list)}')
                if str(problem) in student['solved']:
                    print('**************************************************')
                    print('ENTERING FIRST CONDITION\n')
                    try:
                        sub_time = time.mktime(student['solved'][str(problem)]['submissionTime'].timetuple())
                    except Exception as e:
                        print(f'Error: {e}')
                        pprint(student)
                    # print(f'Problem: {problem} found in {student["first"]}s data')
                    penalty = .15 if sub_time > due_time  else 0.0
                  
                    if not assignment_number in student['required_assns'] and (req_solves > 0):
                        req_solves = req_solves - 1
                        print('**************************************************')
                        print('ENTERING SECOND CONDITION\n')
                        student['required_assns'][assignment_number]={
                            "problem_number": [problem],
                            "on_time": [False if sub_time > due_time else True],
                            "due_time": [due_time],
                            "submitted": [sub_time],
                            "points" : [weight[i] * (num_pnts[problem] - (num_pnts[problem] * penalty))]
                        }
                    elif (req_solves > 0) and (assignment_number in student['required_assns']):
                        print('**************************************************')
                        print('ENTERING THIRD CONDITION\n')
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
                                .append(weight[i] * (num_pnts[problem] - (num_pnts[problem] * penalty)))
                        except Exception as e:
                            print(f'ERROR: {e}')
                            print(f'Problem {problem}')
                            print(f'The value of I is {i}')
                            print(len(weight), len(num_pnts))
                            time.sleep(3)
                else:
                    print('**************************************************')
                    print('ENTERING FOURTH CONDITION\n')
                    student['required_assns'][problem['problem_num']]= problem
                    print('***************************************************')
                    # pprint(student)
                    # print('***************************************************')

        self.collection.update_one({"_id":student["_id"]},{"$set":{"required_assns":student['required_assns']}})
        

    def get_submissions_by_class(self, class_name):
        self.db = self.client['class']
        self.collection = self.db[class_name]
        cursor = list(self.collection.find({},{"_id":0}))
        return cursor
    
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
        print(f'IN UTILIties, get class list {classes}')
        return classes
    def get_class_problems(self, class_name):
        self.db = self.client['assignments']
        self.collection = self.db[class_name]
        assignments = list(self.collection.find({},{"_id":0}))
        return assignments
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
        
    def get_all_student_data(self, class_name):
        self.db = self.client['class']
        self.collection = self.db[class_name]

        student_data = list(self.collection.find({},{"_id":0}))
        for student in student_data:
            pprint(student)
            


    def update_class_submissions(self,  class_name):

        # get list of all assignment problems for class
        self.db = self.client['problem_lists']
        self.collection = self.db[class_name]
        #collect all assignment numbers, turn into one list
        problem_list = list(self.collection.find({},{"_id":0}))
        print('Beginning update operation')
        pprint(problem_list)
        problem_nums = []
        for number in problem_list[0]['problems']:
            problem_nums.append(number)
        # for k, v in problem_list[0].items():
        #     for item in v:
        #         print(f'item = {item}')
        #         problem_nums.append(item)
        
        print(f'problem_nums = {problem_nums}' )
        
        
 
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
                #Collect all student submission, and store in DB
                self.collect_student_submissions(student, problem_nums, class_name)
                result = self.update_student_submissions(student, problem_nums, class_name)
                #result_list.append(result)    
        else:
            return f'Non-Existent collection: {class_name}'
        return result_list
        

    def collect_student_submissions(self, student, problemnums,class_name):
        # use to retrieve probleminfo, title, id, num
        
        problem_list = [
            'submissionID',
            'problemNum',
            'verdictID',
            'runtime',
            'submissionTime',
            'languageId',
            'submissionRank'
        ]
        student_id = student['judgeID']
        #create string of problemnums for uva_api
        problemnums = [str(element) for element in problemnums]
        problemstring = ','.join(problemnums)

        # format url for uva_api
        url = f'https://uhunt.onlinejudge.org/api/subs-nums/'\
              f'{student_id}/{problemstring}/0'
        print(f'URL = {url}')
        id_lookup_db = self.client['id_lookup']
        collection = id_lookup_db['problems']
        result = requests.get(url)
        result = json.loads(result.content.decode())
        temp_dict = []
        for k,v in result.items():
            
            for key, value in v.items():
                if key == 'subs':
                    for item in value:
                        
                        temp_item = dict(zip(problem_list,item ))
                        pprint(f'ITEM IS:\n{temp_item}')
                        del temp_item['submissionID']
                        # del temp_item['submissionTime']
                        del temp_item['submissionRank']
                        temp_item['percent'] = self.grade_percentage[temp_item['verdictID']]
                        num = collection.find_one({'problem_id':temp_item['problemNum']})
                        
                        temp_item['problemNum'] = num['problem_num']
                        temp_item['problemID'] = num['problem_id']
                        temp_item['title'] = num['title']
                        
                        
                        #temp_item['problemNum'] = num
                        temp_dict.append(temp_item)
            #append raw data for later verification
            #!REMOVE THIS AFTER VERIFY
            if temp_dict:
                
                student_name= f'{student["first"]} {student["last"]}'
                new_dict = {}
                new_dict["name"] = student_name
                new_dict["solutions"] = temp_dict
               
                self.collection = self.db[f'raw_data_{class_name}']
                self.collection.insert_one(new_dict)

    def update_student_submissions(self, single_student, problemnums, class_name):
        # Get ID/NUM LOOKUP Collection
        id_lookup_db = self.client['id_lookup']
        lookup_collection = id_lookup_db['problems'] 

        # Get all student submissions collections
        class_db = self.client['class']
        submit_collection = class_db[f'raw_data_{class_name}'] 
        
        #Get specific student submissions
        student_name = f'{single_student["first"]} {single_student["last"]}'
     
        submissions = list(submit_collection.find({'name': student_name},{'_id':1,'name':1, "solutions":1}))
       
        temp_list = {}
        object_id = None
        if submissions:
            for item in submissions:
                #print(item)
                object_id = item['_id']
                #print(object_id)
                for k, v in item.items():
                    if isinstance(v, list):
                        for problem in v:
                            num = str(problem['problemNum'])
                            if not num in temp_list.keys():
                                # problem not in temp dict, add it
                                temp_list[num] = problem
                            elif num in temp_list.keys():
                                # problem in temp dict, compare percent, replace
                                # if new value is larger
                                if temp_list[num]['percent'] < problem['percent']:
                                    del temp_list[num]
                                    temp_list[num] = problem
        print('***************Assignment LIST*******************************')
      
        #collect list of all assignments
        assn_db = self.client['assignments']
        assn_collections  = assn_db[class_name]
        
        
        temp_assn = {}
        assignments = list(assn_collections.find({},{'_id':0}))
        for dictionary in assignments:
            assn_num = dictionary['assn_number']
            uva_ids = dictionary['uva_id']
            print('DICTIONARY IS:')
            print(dictionary)
            for prob_num, prob_data in temp_list.items():
                if int(prob_num) in uva_ids:
                    print(f'STUDENT completed part of  {assn_num}')
                    print(prob_num)
                    print(prob_data)
                    index: int = None
                    for i in range(len(dictionary['uva_id'])):
                        if int(dictionary['uva_id'][i]) == int(prob_num):
                            index = i
                            print(f'INDEX = {index}')
                            break

                    try:
                        if single_student['solved_problems'][assn_num]:
                            print('VALUE ALREADY EXIST')
                            penalty = 0.15 if float(prob_data['submissionTime']) > float(dictionary['unix_datetime']) else 0.0

                            # if error is not thrown key [assn_num] exists
                            single_student['solved_problems'][assn_num]['uva_numbers'].append(int(prob_num))
                            single_student['solved_problems'][assn_num]["percent_achieved"].append(prob_data['percent'] - (prob_data['percent'] * penalty))
                            single_student['solved_problems'][assn_num]['title'].append(prob_data['title'])
                            single_student['solved_problems'][assn_num]['weight'].append(dictionary['weight'][index])
                            achvd = single_student['solved_problems'][assn_num]["achieved"]
                            single_student['solved_problems'][assn_num]["achieved"] = achvd + 1
                            single_student['solved_problems'][assn_num]["complete"] = True if single_student['solved_problems'][assn_num]["achieved"] >= dictionary['required'] else False
                            single_student['solved_problems'][assn_num]['date_time_due'] = dictionary['due_date']
                            single_student['solved_problems'][assn_num]['unix_due_time'] = dictionary['unix_datetime']
                            single_student['solved_problems'][assn_num]['unix_sub_time'] = prob_data['submissionTime']
                            single_student['solved_problems'][assn_num]['penalties'].append(penalty)
                            #********************COKME BAVK
                    except KeyError as KE:
                        # [assn_num] not exists create structure
                        print('VAlue created')
                        penalty = 0.15 if float(prob_data['submissionTime']) > float(dictionary['unix_datetime']) else 0.0
                        single_student['solved_problems'][assn_num]={
                            "assn_num":  assn_num,
                            "uva_numbers" : [int(prob_num)],
                            "percent_achieved": [prob_data['percent'] - (prob_data['percent'] * penalty)],
                            "title" : [prob_data['title']],
                            "weight": [dictionary['weight'][index]],
                            "required": dictionary['required'],
                            "achieved": 1,
                            "complete": True if 1 == dictionary['required'] else False,
                            'date_time_due': dictionary['due_date'],
                            'unix_due_time': dictionary['unix_datetime'],
                            'unix_sub_time': prob_data['submissionTime'],
                            'penalties': [penalty]
                        }
        #start here
        class_collection = class_db[class_name]
        class_collection.update_one({"_id":single_student['_id']},{"$set":{"solved_problems":single_student['solved_problems']}})
       
                



            

        
    def ymdhms_to_timestamp_utc(self,value: str) -> int:
        '''
        https://stackoverflow.com/questions/33621639/convert-date-to-timestamp-in-python
        '''
        print(value)
        naive_dt = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        utc_dt = naive_dt.replace(tzinfo=timezone.utc)
        return int(utc_dt.timestamp())

    # def add_class_problem(self, db, collection, problem):
    #     print('***********************************************************')
    #     ydhms = self.ymdhms_to_timestamp_utc(
    #         f'{problem.due_date} {problem.time_due}:00')
    #     problem.unix_datetime = str(ydhms)
    #     problem = problem.dict()
    #     print(type(problem))
    #     pprint(problem)
        
       
   
    def add_class_problem(self, db, collection, problem):
        # set db and collection for assignments
        self.db = self.client[db]
        self.collection = self.db[collection]
        problem_list = []
        error_list = []
        
        
        print(type(problem))
        problem_list.extend(problem.uva_id)
        pprint(f'PROBLEM LIST {problem_list}')
        times_string= f'{problem.due_date}'
        print(times_string)
        ydhms = self.ymdhms_to_timestamp_utc(times_string)
        problem.unix_datetime = str(ydhms)
        problem = problem.dict()
        try:
            result = self.collection.insert_one(problem).inserted_id
        except Exception as E:
            error_list.append(E)
        print(f'RESULT ={result}')
        # set db and collection for problem list for the class
        self.db = self.client['problem_lists']
        self.collection = self.db[collection]
        if_exists = self.collection.find_one({'semester':collection})
        print(f'IF exists = {if_exists}')
        print(problem_list)
        if(if_exists == None):
            print(f'IF_EXISTS == FALSE {if_exists}')
            self.collection.insert_one({"semester": collection,"problems": problem_list})
        else:
            print(f'IF_EXISTS == TRUE')
            
            self.collection.update_one(
                {"semester":collection},
                    {"$addToSet":
                        {"problems":
                            {"$each": problem_list}
                        }
                    }
            )
        return {
            "status": "OK" if result else "FAILED",
            "data": str(result) if result else None,
            "error": None if len(error_list) == 0 else error_list
        }
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
            #Create dictionary of {uva_id: percentage_value} for each assn
            #append that to each assignment in assignments for easier access 
            #in grading 
            '''
            # uva_percentages[assignment['assignment']] = dict(zip(assignment['uva_id'], assignment['percentage']))
            # assignment['grade_criteria'] = uva_percentages[assignment['assignment']]
            id_list = assignment['uva_id']
            for i in range(0, len(id_list)):
                id_list[i] = int(id_list[i])
            uva_percentages.append( dict(zip(assignment['uva_id'], assignment['percentage'])))
            
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
    #uvautil.set_problem_list()
    
    #print(uvautil.get_class_problems('Fall_2021'))
    
    a4 =Assignment(assn_number="A04",
        title=["Hashmat the brave warrior"],
        required=1,
        uva_id=[10055],
        percent=[1.0],
        due_date = str(datetime.datetime(2021,8,31,14,0)),
        
        weight =[100]
    )
    a5=Assignment(
        assn_number ="A05",
        title=["Traffic Lights"],
        required= 1,
        uva_id=[161],
        percent=[1.0],
        due_date=str(datetime.datetime(2021, 9,7,23,59)),
        weight=[100]
    )
    a6=Assignment(assn_number ="A06",
        title=["Jolly Jumpers"],
        required=1,
        uva_id=[10038],
        percent=[1.0],
        due_date= str(datetime.datetime(2021,9,9,15,20)),
       
        weight=[100]
    )
    a7= Assignment( assn_number="A07", title=["Place the Guards"],
        required=1,
        uva_id=[11080],
        percent=[1.0],
        due_date= str(datetime.datetime(2021,9,9,15,20)),
       
        weight=[100])
    a8=Assignment(assn_number="A08",
        title=["Hardwood Species","Football Problem"],
        required=2,
        uva_id=[10226,10194],
        percent=[.5, .5],
        due_date= str(datetime.datetime(2021,9,21,15,20)),
        
        weight=[50,50]
    )
    a9 = Assignment(assn_number="A09",
        title=["Towers of Hanoi"],
        required=1,
        uva_id=[10017],
        percent=[1],
        due_date= str(datetime.datetime(2021,9,28,15,20)),
        
        weight=[100]
    )
    a10=Assignment(assn_number="A10",
        title=["Brick Wall Patterns", "Sunny Mountains"],
        required=1,
        uva_id=[900,920],
        percent=[.5, .5],
        due_date= str(datetime.datetime(2021, 9, 30,15,20)),
       
        weight=[50,50]
    )
    a11=Assignment(assn_number="A11",
        title=["Maximum Sum"],
        required=1,
        uva_id=[108],
        percent=[1],
        due_date= str(datetime.datetime(2021, 10, 7,15,20)),
       
        weight=[100]
    )
    a13=Assignment(assn_number="A13",
        title=["Mice and Maze"],
        required=1,
        uva_id=[1112],
        percent=[1.0],
        due_date= str(datetime.datetime(2021, 10, 26, 15, 20)),
      
        weight=[100]
    )
    a14=Assignment(assn_number="A14",
        title=["3n + 1", "TEX Quotes", "Skew Binary", "Primary Arithmetic",
                "Hashmat the brave Warrior","Back to Highschool Physics",
                "Summation of Polynomials","Peters Smokes","Above Average",
                "Back to Intermediate Math", "Odd Sum", 
                "Parity","Searching for Nessy", "Relation Operator", 
                "Division of Nlogonia", "Automatic Answer","Etruscan Warriors",
                "Hello World","Cost Cutting","Jumping Mario","Automate the Grades",
                "Horror Dash","Bafana Bafana","Egypt","Brick Game","Language Detection",
                "One-Two-Three","Save Setu", "Hajj-e-akbar","10:6:2"],
        required=3,
        uva_id=[100,
                272,
                575,
                10035,
                10055,
                10071,
                10302,
                10346,
                10370,
                10773, 
                10783,
                10931,
                11044,
                11172,
                11498,
                11547,
                11614,
                11636,
                11727,
                11764,
                11777,
                11799,
                11805,
                11854,
                11875,
                12250,
                12289,
                12403,
                12577,
                12578],
        percent=[.3333,.3333,.3333,.3333,.3333,.3333,.35,.3333,.3333,.3333,
                      .3333,.3333,.98,.3333,.75,.3333,.3333,.3333,.3333,.3333,
                      .3333,.3333,.3333,.3333,.3333,.5,.3333,.3333,.3333,1],
        due_date= str(datetime.datetime(2021, 11, 21,15,20)),
      
        weight=[33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,
                  33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,
                  33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3,33.3]
    )
    a17=Assignment(
        assn_number="A17",
        title=["Tree Summing"],
        required=1,
        uva_id=[112],
        percent=[1],
        due_date= str(datetime.datetime(2021, 11, 23,15,20)),
        
        weight=[100]
    )
    
    
    # *******************************************
    uvautil.add_class_problem('assignments','Fall_2021',a4)
    uvautil.add_class_problem('assignments','Fall_2021',a5)
    uvautil.add_class_problem('assignments','Fall_2021',a6)
    uvautil.add_class_problem('assignments','Fall_2021',a7)
    uvautil.add_class_problem('assignments','Fall_2021',a8)
    uvautil.add_class_problem('assignments','Fall_2021',a9)
    uvautil.add_class_problem('assignments','Fall_2021',a10)
    uvautil.add_class_problem('assignments','Fall_2021',a11)
    uvautil.add_class_problem('assignments','Fall_2021',a13)
   
    uvautil.add_class_problem('assignments','Fall_2021',a14)
    uvautil.add_class_problem('assignments','Fall_2021',a17)
    uvautil.update_class_submissions('Fall_2021')
    

   