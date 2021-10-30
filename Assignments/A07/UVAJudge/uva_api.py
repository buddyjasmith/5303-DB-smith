import csv
from fastapi import FastAPI, Form, HTTPException, Response
from typing import Optional, List
from fastapi.responses import JSONResponse, FileResponse

from CSVUtilities import CSVUtil
from pprint import pprint
import json
import uvicorn
from fastapi.encoders import jsonable_encoder

app = FastAPI()
csv_utils = CSVUtil()

@app.get("/")
def home():
    return {"message": "Sucess"}

@app.get('/class/{class_name}')
def get_class_by_name(class_name: str):
    status = csv_utils.get_class(class_name)
    return status

@app.post('/new_class/{document_id}/{file_name}/{semester}')
def create_new_class(document_id: str, file_name: str, semester: str):
    response = csv_utils.start_new_class(document_id, file_name, semester)
    print(response)
    return response
@app.get('/all_classes')
def get_all_classes():
    response = list(csv_utils.get_all_classes())
    return response
@app.get('/pdf/{problem_id}')
def get_pdf_by_num(problem_id: int):
    response = csv_utils.get_pdf_by_number(problem_id)
    # print(type(response))
    # return_val =""
    # for item, value in response.items():
    #     if(item == 'Data'):
    #         for val in value:
    #             print(val.read())
    return Response(response)

@app.put('update_class_submissions/{semester}/{class_name}')
def update_class_submissions(semester: str, class_name: str):
    response = csv_utils.update_class_submissions(semester, class_name)
    
@app.put('/store_pdf/{number}')
def save_pdf_by_number(number: int):
    response = csv_utils.download_problem_pdf(number)
    return response
if __name__=="__main__":
    uvicorn.run("uva_api:app", host="0.0.0.0", port=8004, log_level="info", reload=True)