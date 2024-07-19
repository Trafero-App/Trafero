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
    if route_file_name is None:
        return {"Message": "Route not found."}
    route_file_name = route_file_name["file_name"]
    
    try:
        route_geojson = await db.get_route_geojson(route_file_name)
    except FileNotFoundError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Message": "Route is defined in the database, but the file is not found. Contact backend."}
    
    return {"Message" : "All Good.", "route_data": route_geojson}


@app.get("/available_vehicles/{route_id}", status_code=status.HTTP_200_OK)
async def available_vehicles(route_id:int, response: Response, long:float|None=None, lat:float|None = None):
    
    vehicles = await db.get_route_vehicles(route_id)
    if vehicles is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Message": "Route not found."}
    print(vehicles)
    
    try:
        route_file_name = await db.get_route_file_name(route_id)
    except FileNotFoundError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Message": "Route is defined in the database, but the file is not found. Contact backend."}
    

    route_file_name = route_file_name["file_name"]
    route_geojson = await db.get_route_geojson(route_file_name)

    route = route_geojson["features"][0]["geometry"]["coordinates"]

    projection_indices = {}
    for vehicle in vehicles:

        projection_index = helper.project_point_on_route((vehicle["longitude"], vehicle["latitude"]), route)
        vehicle["projection_index"] = projection_index

    projected_pick_up_point_index = helper.project_point_on_route((long, lat), route)

    available_vehicles = sorted(vehicles, key=lambda x: x["projection_index"], reverse = True)
    for i, vehicle in enumerate(available_vehicles):
        if vehicle["projection_index"] <= projected_pick_up_point_index:
            available_vehicles = available_vehicles[i:]
            for vehicle2 in available_vehicles:
                del vehicle2["projection_index"]
            break
    return {"Message" : "All Good.", "available_vehicles" : available_vehicles}