from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
import asyncpg
import os
from dotenv import load_dotenv, find_dotenv

from validation_classes import Point, vehicle_location

import geojson

import helper

# For data validation


# Get access credentials to database
load_dotenv(find_dotenv())
DB_URL = os.getenv("db_url")

# Open connection to database when app starts up
# and close the connection when the app shuts down
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(DB_URL)
    # app.state.db.fetch()
    yield
    print("Closing app...")
    await app.state.db_pool.close()


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
    async with app.state.db_pool.acquire() as con:
        entry = await con.fetchrow("SELECT * FROM vehicle_location WHERE vehicle_id=$1", vehicle_id)
    if entry is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Message" : "Error: Vehicle location is not available."}
    
    
    return {"longitude": entry["longitude"], "latitude" : entry["latitude"], "Message": "All Good 👍"}

@app.post("/vehicle_location", status_code=status.HTTP_200_OK)
async def post_vehicle_location(vehicle_location_data: vehicle_location, response: Response):
    vehicle_id, latitude, longitude = vehicle_location_data.id, vehicle_location_data.latitude, vehicle_location_data.longitude
    try:
        async with app.state.db_pool.acquire() as con: 
            await con.execute("""INSERT INTO vehicle_location 
                                (vehicle_id, latitude, longitude) VALUES ($1, $2, $3)""", vehicle_id, latitude, longitude)
        return {"Message": "All Good 👍"}
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
    async with app.state.db_pool.acquire() as con:
        result = await con.execute("""UPDATE vehicle_location SET longitude=$1, 
                                            latitude=$2 WHERE vehicle_id=$3""", longitude, latitude, vehicle_id)
    # False signifies that you tried to update the location of a vehicle whose location isn't in the db yet
    if result == "UPDATE 0":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Message" : """Error: You have attempted to update the location of a vehicle who's location hasn't been added.
                            Maybe you mean to send a POST request?"""}
    else:
        return {"Message": "All Good 👍"}

@app.get("/route/{requested_route_id}", status_code=status.HTTP_200_OK)
async def route(requested_route_id: int, response: Response):
    async with app.state.db_pool.acquire() as con:
        route_file_name = await con.fetchrow("SELECT file_name FROM route WHERE id=$1", requested_route_id)
    if route_file_name is None:
        return {"Message": "Invalid route id. Not found in database."}
    route_file_name = route_file_name["file_name"]
    
    try:
        route_file = open("routes/" + route_file_name)
    except FileNotFoundError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Message": "Route is defined in the database, but the file is not found. Contact backend."}
    
    geojson_route_data = dict(geojson.load(route_file))
    route_file.close()
    return {"Message" : "All Good.", "route_data": geojson_route_data}








#############################################################################################################


@app.get("/available_vehicles/{route_id}", status_code=status.HTTP_200_OK)
def available_vehicles(route_id:int, pick_up_point:Point|None=None):

    vehicles_list = input ()   #data base according to route_number (ID,lon,lat)
    vehicles = []
    way_points = input()       #data base list of waypoints (this list should contain points of form A(lon,lat,index in geojson))

    route = input ()           #geojson file according to route_number







    # ASSOCIATING EACH VEHICLE TO A POINT AND SAVING THE INDEX
    for vehicle in vehicles_list:

        index = helper.project_point_on_route(vehicle[1:3], route)
        vehicles.append(vehicle+(index,))      #(ID, lon, lat, index)


    # ASSOCIATING THE PICK UP POINT TO A POIT AND SAVING THE INDEX
    projected_pick_up_point = helper.project_point_on_route(pick_up_point, route)


    # SORTING THE VEHICLES FROM CLOSEST TO FARTHEST
    available_vehicles = sorted(vehicles, key=lambda x: x[3], reverse = True)
    for i in range (len(available_vehicles)):
        if available_vehicles[i][3] <= projected_pick_up_point:
            available_vehicles = available_vehicles[i:]
            break