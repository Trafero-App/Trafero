from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
import asyncpg
import os
from dotenv import load_dotenv, find_dotenv

from validation_classes import Point, vehicle_location

import geojson

import helper
from db_layer import db
# For data validation


# Get access credentials to database
load_dotenv(find_dotenv())
DB_URL = os.getenv("db_url")

# Open connection to database when app starts up
# and close the connection when the app shuts down
@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect(DB_URL)

    yield
    
    await db.disconnect()


app = FastAPI(lifespan=lifespan)

# Allow only specific origins to make requests
origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # allow requests from the specified origins
    allow_credentials=True, # allow credentials to be sent (e.g cookies)
    allow_methods=["*"], # allow POST, GET, PUT ... `*` is "all"
    allow_headers=["*"]

)


@app.get("/vehicle_location/{vehicle_id}", status_code=status.HTTP_200_OK)
async def get_vehicle_location(vehicle_id: int, response: Response):
    entry = await db.get_vehicle_location(vehicle_id)
    if entry is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Message" : "Error: Vehicle location is not available."}
    
    
    return {"longitude": entry["longitude"], "latitude" : entry["latitude"], "Message": "All Good."}

@app.post("/vehicle_location", status_code=status.HTTP_200_OK)
async def post_vehicle_location(vehicle_location_data: vehicle_location, response: Response):
    vehicle_id, latitude, longitude = vehicle_location_data.id, vehicle_location_data.latitude, vehicle_location_data.longitude
    try:
        await db.add_vehicle_location(vehicle_id, longitude=longitude, latitude=latitude)
        return {"Message": "All Good."}
    except asyncpg.exceptions.UniqueViolationError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
                "Message":
                """Error: You have attempted to add the location of a vehicle who's location has already been added. Maybe you meant to send a PUT request?"""
                }
    except asyncpg.exceptions.ForeignKeyViolationError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Message": "Error: You have attempted to add the location of a vehicle that doesn't exist."}


@app.put("/vehicle_location", status_code=status.HTTP_200_OK)
async def post_vehicle_location(vehicle_location_data: vehicle_location, response: Response):
    vehicle_id, latitude, longitude = vehicle_location_data.id, vehicle_location_data.latitude, vehicle_location_data.longitude
    result = await db.update_vehicle_location(vehicle_id, longitude=longitude, latitude=latitude)
    # False signifies that you tried to update the location of a vehicle whose location isn't in the db yet
    if result == "UPDATE 0":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Message" : """Error: You have attempted to update the location of a vehicle who's location hasn't been added.
                            Maybe you mean to send a POST request?"""}
    else:
        return {"Message": "All Good."}

@app.get("/route/{requested_route_id}", status_code=status.HTTP_200_OK)
async def route(requested_route_id: int, response: Response):
    route_file_name = await db.get_route_file_name(requested_route_id)
    print("#############################################################################################################################")
    if route_file_name is None:
        return {"Message": "Invalid route id. Not found in database."}
    print("#############################################################################################################################")
    route_file_name = route_file_name["file_name"]
    
    try:
        route_geojson = await db.get_route_geojson(route_file_name)
    except FileNotFoundError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Message": "Route is defined in the database, but the file is not found. Contact backend."}
    
    print("#############################################################################################################################", type(route_geojson))
    return {"Message" : "All Good.", "route_data": route_geojson}


# @app.get("/available_vehicles/{route_id}", status_code=status.HTTP_200_OK)
# async def available_vehicles(route_id:int, response: Response, pick_up_point:Point|None=None):
#     async with app.state.db_pool.acquire() as con: 
#         # data base according to route_number (ID,lon,lat)
#         vehicle_list = await con.fetch(""" SELECT (vehicle_id, longitude, latitude) FROM vehicle_location WHERE 
#                                         vehicle_id IN (
#                                                 SELECT id FROM vehicle WHERE route_id = $1
#                                         )""", route_id)
#         vehicle_list = [tuple(vehicle_info[0]) for vehicle_info in vehicle_list]
#         route_file_name = await con.fetchrow("SELECT file_name FROM route WHERE id=$1", route_id)
#         if route_file_name is None:
#             return {"Message": "Invalid route id. Not found in database."}
#         route_file_name = route_file_name["file_name"]
        
#         try:
#             route_file = open("routes/" + route_file_name)
#         except FileNotFoundError:
#             response.status_code = status.HTTP_404_NOT_FOUND
#             return {"Message": "Route is defined in the database, but the file is not found. Contact backend."}
        
#         geojson_route_data = dict(geojson.load(route_file))
#         route_file.close()
#         route = geojson_route_data["features"][0]["geometry"]["coordinates"]
#         print(route)
#         print()
#         print()
#         print()
#         print()
#         print()
#     vehicles = []
#     way_points = input()       #data base list of waypoints (this list should contain points of form A(lon,lat,index in geojson))


#     # ASSOCIATING EACH VEHICLE TO A POINT AND SAVING THE INDEX
#     for vehicle in vehicle_list:

#         index = helper.project_point_on_route(vehicle[1:3], route)
#         vehicles.append(vehicle+(index,))      #(ID, lon, lat, index)


#     # # ASSOCIATING THE PICK UP POINT TO A POIT AND SAVING THE INDEX
#     projected_pick_up_point = helper.project_point_on_route(pick_up_point, route)


#     # # SORTING THE VEHICLES FROM CLOSEST TO FARTHEST
#     available_vehicles = sorted(vehicles, key=lambda x: x[3], reverse = True)
#     for i in range (len(available_vehicles)):
#         if available_vehicles[i][3] <= projected_pick_up_point:
#             available_vehicles = available_vehicles[i:]
#             break