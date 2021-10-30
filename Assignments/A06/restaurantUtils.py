import json
from pymongo import MongoClient
from pprint import pprint

class RestaurantUtils:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client.NYC
        self.collection = self.db.geo_restaurant
    def convertToGeoJSON(self):
        '''
        : @param: None
        : Description: Removes resturants from the file restaurant.json
        :              that are lacking proper coordinates.  Restaurants with 
        :              coordinates have a proper GeoJson structure appended to 
        :              the object and a new list of the items are created.  
        :              When all items have been iterated over.  The new items
        :              are wrote to the file restaurantData.json
        '''
        restaurantsList = []
        coords = []
        with open('restaurant.json') as file:
            for restaurant in file:
                restDict = json.loads(restaurant)
                coords = restDict["address"]["coord"]
                if coords:
                    restDict["location"] = {
                        "type" : "Point",
                        "coordinates" : coords,
                    }
                    del restDict["address"]["coord"]
                    restaurantsList.append(restDict)
        with open('restaurantData.json', 'w+') as new_file:
            for newRestaurant in restaurantsList:
                rest_obj = json.dump(newRestaurant, new_file)

    #!*************************************************************************
    def find_all(self,page_size, page_num):
        '''
        : @params: page_size -> INT -> number of items on each page to be retrn
        : @params: page_num -> INT -> which page to return
        : Description:  The function calculates number of items of which to 
        :               skip when the query is performed.   Then the number of 
        :               items(page_size) are returned to the user. MONGO OBJECT 
        :               ID is not returned
        : TODO: NOT Effecient due to heuristic pagination algo.  Entire list 
        :       must be returned
        : Returns:  List of restaurants
        '''
        skips = page_size * (page_num -1)
        cursor = self.collection.find({},{"_id":0}).skip(skips).limit(page_size)
        return list(cursor)

    #!*************************************************************************
    def get_by_cuisine(self,restaurant_type):
        '''
        : @params: restaurant_type -> string:  Cuisine type. Ex.. Coffee, 
        :          steakhouse, etc...
        : Description:  all restaurants of type cuisine are returned:  MONGO 
        :               OBJECT ID is not returned along with restaurants object
        : Returns:  List of restaurants
        : TODO: NONE
        '''
        results = self.collection.find({"cuisine": restaurant_type},{"_id":0})
        return list(results)

    #!*************************************************************************
    def get_unique_categories(self):
        '''
        : @params: NONE
        : Description: collects a list of unique restaurant categories
        : Returns:  List of restaurants
        : TODO: NONE
        '''
        cursor = self.collection.distinct("cuisine")
        return list(cursor)

    #!*************************************************************************
    def get_by_zip_code(self,zip_list):
        '''
        : @params: zip_list -> List[string].  List of zipcodes
        : Description: searches for restaurants located within the zipcodes
        :              contained in the zip_LIST
        : Returns:  List of restaurants
        : TODO: NONE
        '''
        temp = self.collection.find(
            {'address.zipcode':
                {'$in': zip_list}},
                {"_id":0}
        )
        temp=list(temp)
        
        return temp
    def get_by_distance(self, distance, coords, category=None):
        '''
        : @params: distance -> int: represents the maximum distance to be 
        :          search.  Number should be in kilometers
        : @params: coors -> List[int]: contains a list represent lattitude and
        :          longitude coordinates
        : @parms: category -> OPTIONAL -> String: type of cuisine
        : Description: a search is performed on the database within a certain
        :              distance of the passed coordinates.  Results can be 
        :              further narrowed by searching for specific cuisine types
        : Returns:  List of restaurants
        : TODO: NONE
        '''
        geo_object = {}
        geo_object = { "near": {"type": "Point","coordinates" : coords},
                    "distanceField" : "dist.calculated",
                    "maxDistance": distance,
                    "includeLocs" : "dist.location",
                    "spherical" : "true"
                    }
        if(category):
            geo_object["query"]= {"cuisine" : category}
        
        cursor = self.collection.aggregate([{"$geoNear": geo_object},{"$unset": "_id"}])
        cursor = list(cursor)
    
        return cursor


if __name__ == '__main__':
    #! ***********************************************************************#
    # Convert JSON to correct data fields for geojson
    #convertToGeoJSON()

    # client = MongoClient("mongodb://localhost:27017/")
    # db = client.NYC
    # collection = db.geo_restaurant
    utils = RestaurantUtils()
    # #! ***********************************************************************#
    # Collect paginated results
    # results = utils.find_all(10, 3)
    # pprint(len(results))

    #! ***********************************************************************#
    # Find restaurants by cuisine
    # restaurant = "Bakery"
    # results = utils.find_by_cuisine(restaurant)
    # pprint(results)

    #! ***********************************************************************#
    # Find unique categories of restaurant
    # results = utils.get_unique_categories()
    # pprint(results)

    #! ***********************************************************************#
    # Find restaurants by zipcode 
    zip_list = []
    zip_list.append("11234")
    results = utils.get_by_zip_code(zip_list)
    pprint(results)

    #! ***********************************************************************#
    # # get by distance
    # results = utils.get_by_distance( 2000,[-73.856077,40.848447],"Café/Coffee/Tea")
    # pprint(len(results))
