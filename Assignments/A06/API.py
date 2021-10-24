from restaurantUtils import RestaurantUtils

import uvicorn
import os
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
# from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
# from typing import Optional, List
import motor.motor_asyncio

app=FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/NYC")
db = client.NYC
collection = db.updated_restaurant

# class PyObjectId(ObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid objectid")
#         return ObjectId(v)

#     @classmethod
#     def __modify_schema__(cls, field_schema):
#         field_schema.update(type="string")
@app.get("/hello")
async def root():
    return {"message": "Hello World"}

if __name__=="__main__":
    uvicorn.run("API:root", host="0.0.0.0", port=8000, log_level="info")