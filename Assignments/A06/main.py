from fastapi import FastAPI, Form, HTTPException, Response, Body
from typing import Optional, List
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from models import Geo_Restaurant
from restaurantUtils import RestaurantUtils
from pprint import pprint
import json
from fastapi.encoders import jsonable_encoder
# from bson.objectid import ObjectId

import uvicorn

app = FastAPI()
utils = RestaurantUtils()

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

@app.get("/")
def home(important: str=Body(...), item: Item = Body(...)):
    return {"message": item, 
            "important": important}

@app.get('/restaurants/')
async def get_all(page_size: int = Form(...), page_num: int = Form(...)):
    '''
    : Form-Data: 
    :   @param -> page_size: Number of restaurants to be returned per page
    :   @param: -> page_num: Page number to return to results
    : Description:
    :   When the route '/restaurants/' is passed along with page_num and 
    :   'page_size', the restaurantUtils class is called and returns a list
    :   of the size 'page_size' located at 'page_num'.  The results are 
    :   returned to the caller in json format under response['data']
    : 
    '''
    description = "Paginated results of all Restaurants in NYC"
    cursor =  list(utils.find_all(page_size, page_num))
    return {
        "status": 1 if len(cursor) > 0 else 0,
        "description": description,
        "size": len(cursor),
        "response": {
            "data": cursor
        }
    }

@app.get(
    '/get_by_distance/',
    response_description="List of all restaurants within a given distance"
    )
async def get_by_distance(distance: int = Form(...), 
                          coords: List[float] = Form(...),
                          category: Optional[str]=Form(None)):
    '''
    : Form-Data:
    :   @param: distance -> distance from coordinates to be searched.  INT
    :   @param: coords -> List containing floats representing longitude and 
    :           latitude. This represents the location to find restaurants near
    :           or within the specified distance.  LIST
    :   @param: category(OPTIONAL) -> can be used to narrow the search to a 
    :           specific category of restaurants near coordinates supplied by
    :           the caller
    :   Description: Route checks for restaurants near the coordinates provied 
    :                by the caller within a specified distance.  Results can be
    :                narrowed by supplying an optional "category" of restaurant
    :   Returns:
    :       JSON object containing a list of restaurants
    '''
    description = "List of all restaurants within a given distance"
    cursor = list(utils.get_by_distance(distance, coords, category))
    return {
        "status": 1 if len(cursor) > 0 else 0,
        "description": description,
        "size": len(cursor),
        "response": {
            "data": cursor
        }
    }

@app.get('/zipcode/', response_description="Get restaurants locted within a list of zipcodes")
async def get_by_zipcode(ziplist: List[str] = Form(...)):
    '''
    : Form-Data:
    :   @param: ziplist -> List containing strings representing zipcodes.
    :   Description: Route checks for restaurants located within the zipcodes
    :                of the passed list.
    :   Returns:
    :       JSON object containing a list of restaurants
    '''
    description ="Get restaurants locted within a list of zipcodes"
    
    cursor = utils.get_by_zip_code(ziplist)
    cursor = list(cursor)
    return {
        "status": "Success" if len(cursor) > 0 else "Failed",
        "description": description, 
        "size": len(cursor),
        "response": cursor
        }
@app.get('/categories')
async def get_categories():
    
    '''
    : Form-Data:
    :   @param:  None
    :   Description: returns a list of unique restaurant categories located 
    :                within the database
    :   Returns:
    :       JSON object containing a list of strings of unique restaurant 
    :       categories
    '''
    descriptions = "Returns a list of all categories of restaurants in NYC"
    cursor = utils.get_unique_categories()
    cursor = list(cursor)
    return {
        "status": 200 if len(cursor) > 0 else 404,
        "description": descriptions, 
        "size": len(cursor),
        "response": cursor
        }
@app.get(
    '/cuisine_look_up', 
    )
async def get_cuisine(cuisine: str = Form(...)):
    cursor = list(utils.get_by_cuisine(cuisine))
    cursor = jsonable_encoder(cursor)
    description = "List of restaurants of a given type"
    # return JSONResponse(content=cursor)
    return {
        "status": 200 if len(cursor) > 0 else 404,
        "description": description,
        "size": len(cursor),
        "response": {
            "data": cursor
        }
    }
    


if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, log_level="info", reload=True)