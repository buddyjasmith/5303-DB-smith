

from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from typing import Optional, List
from datetime import datetime, time, timedelta
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")
class Address(BaseModel):
    building: str 
    street: str 
    zipcode: str 
class Grade(BaseModel):
    date: datetime
    grade: str 
    score: int
class Location(BaseModel):
    type: str 
    coordinates: List[float]

class Geo_Restaurant(BaseModel):
    address: Address = None
    borough: str
    cuisine: str 
    grades: List[Grade] = []
    location: Location = None
    name: str
    restaurant_id: str
    class Config:
        orm_mode = True
        
    

