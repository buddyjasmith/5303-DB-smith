import csv
from hmac import new
import secrets
from http.client import responses
from fastapi import FastAPI, Form, HTTPException, Response, Body, Depends, HTTPException, status
from typing import Optional, List
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from UVAUtilities import UVAUtil
from pprint import pprint
import json

import uvicorn
import datetime
security = HTTPBasic()
from fastapi.encoders import jsonable_encoder
from models import Assignment, ClassModel, PdfModel, UpdateClassModel
app = FastAPI()
uva_utils = UVAUtil()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "TerryGriffin")
    correct_password = secrets.compare_digest(credentials.password, "P4$$W0Rd123")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get('/get_class_data/{class_name}')
def get_class_data(class_name: str, username: str = Depends(get_current_username)):
    student = uva_utils.get_all_student_data(class_name)
    

@app.get("/")
def home(username: str = Depends(get_current_username)):
    return {"message": username}


@app.get("/class_list")
def get_class_list(username:str = Depends(get_current_username)):
    print('I am being called')
    classes = uva_utils.get_class_list()
    pprint(classes)
    return classes


@app.get('/class/{class_name}')
def get_class_by_name(class_name: str, username: str = Depends(get_current_username)):
    print(class_name)
    status =uva_utils.get_class(class_name)
    return status


@app.get('/class_assignments/{class_name}')
def get_assignments(class_name: str, username: str = Depends(get_current_username)):
    print(f'Class name: {class_name} is being called by applicqtion')
    response = uva_utils.get_class_problems(class_name)
    print(response)
    return response


@app.post('/new_class/')
def create_new_class(new_class: ClassModel = Body(...),
                     username:str = Depends(get_current_username)):
    print('*******************************************************')
    print('New classw being called')
    print(new_class)
    
   
    response = uva_utils.start_new_class(new_class.document_id, new_class.semester)
    # print(response)
    # return response
@app.post('/new_assignment/')
def add_new_assignment(new_assignment: Assignment ,username:str = Depends(get_current_username)):
    ...
    print(f'new_assignment is : \n\t{new_assignment}')
    due_date = [str(x) for x in new_assignment.due_date.split('-')]
    time_due = [str(x) for x in new_assignment.time_due.split(':')]
    due_string = f'{",".join(due_date)},{",".join(time_due)} '
    assignment =dict()
    assignment["assignment"]=new_assignment.assn_number,
    assignment["title"]=new_assignment.title,
    assignment["required"]=new_assignment.required,
    assignment["uva_num"]=new_assignment.uva_id,
    assignment["percentage"]=new_assignment.percent,
    assignment["due_date"]=new_assignment.due_date,
    assignment["completed"]= {},
    assignment["weights"]=new_assignment.weight
    assignment["time_due"] = new_assignment.time_due
    print(type(assignment))
    response = uva_utils.add_class_problem('assignments',str(new_assignment.semester),new_assignment)
    return response
   
@app.get('/all_classes')
def get_all_classes():
    response = list(uva_utils.get_all_classes())
    return {
        "data": response
    }
@app.get('/pdf/{problem_id}')
def get_pdf_by_num(problem_id: str):
    print(f'pdf is {problem_id}')
    response = uva_utils.get_pdf_by_number(problem_id)
    # print(type(response))
    # return_val =""
    # for item, value in response.items():
    #     if(item == 'Data'):
    #         for val in value:
    #             print(val.read())
    return Response(response)

@app.put('/update_class/{class_name}')
def update_class_submissions(
        class_name:str,
        credentials: HTTPBasicCredentials = Depends(security)):
    print(class_name)
    response = uva_utils.update_class_submissions(class_name)
    # return{
    #     "status": "Failed" if(not response) else "Success",
    #     "data": response,
    #     "description": "Grade student submissions for a given class",
    #     "example":"147.182.202.105:8004/store_pdf/<PROBLEM NUMBER>",
    #     "parameter": f"class_name: str = semester followed by year, ex. Fall_2021",
    #     "possible return": "True or False"
    # }
@app.put('/store_pdf/{number}')
def save_pdf_by_number(number: int):
    results = uva_utils.download_problem_pdf(number)
    print(results)
    return{
        "status": "Failed" if(not results) else "Sucess",
        "description": "Store uva pdf(s) in the database for later use",
        "example":"147.182.202.105:8004/store_pdf/<PROBLEM NUMBER>",
        "possible return": "True or False"
    }
@app.get('/class_submissions/{class_name}')
def get_class_submissions(class_name: str, username:str = Depends(get_current_username)):
    student_subs = uva_utils.get_submissions_by_class(class_name)
    return student_subs

@app.put('grade_class/{class_name}')
def grade_by_class(class_name:str, username:str = Depends(get_current_username)):
    response = uva_utils.grade_by_class(class_name)
    print(f'RESPONSE = {response}')
if __name__=="__main__":
    uvicorn.run("uva_api:app", host="0.0.0.0", port=8004, log_level="info", reload=True)