import csv
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
security = HTTPBasic()
from fastapi.encoders import jsonable_encoder
from models import NewClassModel, PdfModel, UpdateClassModel
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

@app.get("/")
def home(username: str = Depends(get_current_username)):
    return {"message": username}
@app.get("/class_list")
def get_class_list(username:str = Depends(get_current_username)):
    classes = uva_utils.get_class_list()
    return classes
@app.get('/class/{class_name}')
def get_class_by_name(class_name: str, username: str = Depends(get_current_username)):
    print(class_name)
    status =uva_utils.get_class(class_name)
    return status

@app.post('/new_class/')
def create_new_class(new_class: NewClassModel = Body(...)):
    print(new_class.document_id)
    print(new_class.class_name)
    response = uva_utils.start_new_class(new_class.document_id, new_class.class_name)
    print(response)
    return response
@app.put('/new_assignment')
def add_new_assignment():
    ...
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
    return{
        "status": "Failed" if(not response) else "Success",
        "data": response,
        "description": "Grade student submissions for a given class",
        "example":"147.182.202.105:8004/store_pdf/<PROBLEM NUMBER>",
        "parameter": f"class_name: str = semester followed by year, ex. Fall_2021",
        "possible return": "True or False"
    }
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
if __name__=="__main__":
    uvicorn.run("uva_api:app", host="0.0.0.0", port=8004, log_level="info", reload=True)