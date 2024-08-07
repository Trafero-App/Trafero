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
import json
from fuzzywuzzy import fuzz, process

# Get access credentials to database
load_dotenv(find_dotenv())
DB_URL = os.getenv("db_url")

# Open connection to database when app starts up
# and close the connection when the app shuts down
# Also load routes
@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect(DB_URL)

    app.state.routes = {}
    
    routes_data = await db.get_all_routes_data()
    for route_id, file_name in routes_data:
        route_geojson = await db.get_route_geojson(file_name)
        route_geojson["properties"]["route_id"] = route_id
        app.state.routes[route_id] = route_geojson

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
        return {"message" : "Error: Vehicle location is not available."}
    
    
    return {"message": "All Good.", "longitude": entry["longitude"], "latitude" : entry["latitude"]}

@app.post("/vehicle_location", status_code=status.HTTP_200_OK)
async def post_vehicle_location(vehicle_location_data: vehicle_location, response: Response):
    vehicle_id, latitude, longitude = vehicle_location_data.vehicle_id, vehicle_location_data.latitude, vehicle_location_data.longitude
    try:
        await db.add_vehicle_location(vehicle_id, longitude=longitude, latitude=latitude)
        return {"message": "All Good."}
    except asyncpg.exceptions.UniqueViolationError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
                "message":
                """Error: You have attempted to add the location of a vehicle who's location has
                already been added. Maybe you meant to send a PUT request?"""
                }
    except asyncpg.exceptions.ForeignKeyViolationError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Error: You have attempted to add the location of a vehicle that doesn't exist."}


@app.put("/vehicle_location", status_code=status.HTTP_200_OK)
async def put_vehicle_location(vehicle_location_data: vehicle_location, response: Response):
    vehicle_id, latitude, longitude = vehicle_location_data.vehicle_id, vehicle_location_data.latitude, vehicle_location_data.longitude
    result = await db.update_vehicle_location(vehicle_id, longitude=longitude, latitude=latitude)
    # False signifies that you tried to update the location of a vehicle whose location isn't in the db yet
    if result == "UPDATE 0":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message" : """Error: You have attempted to update the location of a vehicle who's location hasn't been added.
                            Maybe you mean to send a POST request?"""}
    else:
        return {"message": "All Good."}

@app.get("/route/{requested_route_id}", status_code=status.HTTP_200_OK)
async def route(requested_route_id: int, response: Response):
    if requested_route_id not in app.state.routes:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Error: Route not found."}
    
    return {"Message" : "All Good.", "route_data": app.state.routes.get(requested_route_id)}


@app.get("/available_vehicles/{route_id}", status_code=status.HTTP_200_OK)
async def available_vehicles(route_id:int, response: Response,
                             pick_up_long:float|None=None, pick_up_lat:float|None = None): 
    # Load route
    if route_id not in app.state.routes:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Route not found."}
    route_geojson = app.state.routes[route_id]
    
    # Get route vehicles
    vehicles = await db.get_route_vehicles(route_id)
    if vehicles is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No vehicles available on the route with id '" + route_id  + "'.", 

                "available_vehicle" : {}}

    if pick_up_long is not None and pick_up_lat is not None:
        route = route_geojson["geometry"]["coordinates"]
        vehicles, av_vehicles_last_i = helper.filter_vehicles__pick_up((pick_up_long, pick_up_lat), vehicles, route)
        for i in range(av_vehicles_last_i):
            vehicles[i]["passed"] = False

        for i in range(av_vehicles_last_i, len(vehicles)):
            vehicles[i]["passed"] = True

    helper.geojsonify_vehicle_list(vehicles)
    return {"message" : "All Good.", "available_vehicles" : {"type": "FeatureCollection", "features": vehicles}}


@app.get("/time/driving", status_code=status.HTTP_200_OK)
async def vehicle_time(route_id:int, long1:float, lat1:float, long2:float, lat2:float, response: Response):
    # Load route
    if route_id not in app.state.routes:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Route not found."}
    route = app.state.routes[route_id]["geometry"]["coordinates"]
    waypoints = await db.get_route_waypoints(route_id)
    waypoints = helper.trim_waypoints_list(waypoints, (long1, lat1), (long2, lat2), route)
    return {"message": "All Good.", "time_estimation" : helper.get_time_estimation(waypoints, os.getenv("mapbox_token"), "driving")}


@app.get("/time/walking", status_code=status.HTTP_200_OK)
async def vehicle_time(long1:float, lat1:float, long2:float, lat2:float, response: Response):
    return {"message": "All Good.", "time_estimation" : helper.get_time_estimation([(long1, lat1), (long2, lat2)], os.getenv("mapbox_token"), "walking")}
  

@app.get("/nearby_routes", status_code=status.HTTP_200_OK)
async def nearby_routes(long:float, lat:float, radius:float,
                        long2:float | None = None, lat2: float | None = None, radius2: float | None = None):
    routes_geojson = []
    for _, route in app.state.routes.items():
        route_coords = route["geometry"]["coordinates"]
        proj1_i, min_distance1 = helper.project_point_on_route((long, lat), route_coords)
        if long2 is not None and lat2 is not None and radius2 is not None:
            proj2_i, min_distance2 = helper.project_point_on_route((long2, lat2), route_coords)
            if min_distance1 <= radius and min_distance2 <= radius2 and proj1_i < proj2_i:
                routes_geojson.append(route)
        else:
            if min_distance1 <= radius:
                routes_geojson.append(route)

            
    return {"message": "All Good.", "routes": {"type": "FeatureCollection", "features": routes_geojson}}


@app.get("/search/{word}", status_code=status.HTTP_200_OK)
async def search(word: str):
    routes_info = await db.get_routes_info_search()
    sliced_info = await db.get_sliced_info_search()
    busses_info = await db.get_busses_info_search()
    return helper.search(word, routes_info, sliced_info, busses_info)