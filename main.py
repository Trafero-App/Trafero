from typing import Annotated
from fastapi import FastAPI, Response, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
import asyncpg
import os
from dotenv import load_dotenv, find_dotenv

from validation_classes import vehicle_location, Account_Info, Account_DB_Entry, Review


import helper
import authentication
from db_layer import db
from copy import deepcopy
# For data validation
import json
from fuzzywuzzy import fuzz, process

# Get access credentials to database
load_dotenv(find_dotenv())
DB_URL = os.getenv("db_url")

MAPBOX_TOKEN = os.getenv("mapbox_token")

# Open connection to database when app starts up
# and close the connection when the app shuts down
# Also load routes
@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect(DB_URL)

    app.state.routes = {}
    app.state.routes_search_data = []
    routes_data = await db.get_all_routes_data()
    for route_data in routes_data:        
        route_data = {"details": route_data}
        route_geojson = await db.get_route_geojson(route_data["details"]["file_name"])
        del route_data["details"]["file_name"]
        route_data["line"] = route_geojson
        app.state.routes[route_data["details"]["route_id"]] = route_data

        app.state.routes_search_data.append(((route_data["details"]["route_id"],) + tuple(route_data["details"]["description"].split(' - '))))

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

@app.post("/signup", status_code=status.HTTP_200_OK)
async def signup(account_data: Account_Info, response: Response):
    account_type = account_data.account_type
    phone_num_av = await db.check_phone_number_available(account_data.phone_number, account_type)
    username_av = await db.check_username_available(account_data.username, account_type)
    email_av = await db.check_email_available(account_data.email, account_data.account_type)
    if not phone_num_av:
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": "Sign-up failed. Phone number already in use."}
    
    if not username_av:
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": "Sign-up failed. Username already in use."}
    
    if not email_av:
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": "Sign-up failed. Email already in use."}

    password_hash = authentication.hash_password(account_data.password)
    await db.add_account(Account_DB_Entry(
        account_type=account_data.account_type,
        username=account_data.username,
        password_hash=password_hash,
        first_name=account_data.first_name,
        last_name=account_data.last_name,
        phone_number=account_data.phone_number,
        email=account_data.email,
        status=account_data.status,
        cur_route_id=account_data.cur_route_id,
        routes=account_data.routes
                     ))
    

@app.post("/login/{account_type}", status_code=status.HTTP_200_OK)
async def login(account_type: str, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response):
    user = await authentication.get_user(form_data.username, form_data.password, account_type)
    if user is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Invalid credentials."}
    token_data = {"sub": user["username"], "type": account_type}
    access_token = authentication.create_access_token(
        token_data=token_data
    )
    return {"message": "All good.", "token": {"access_token": access_token, "token_type": "bearer"}}



@app.get("/vehicle_location/{vehicle_id}", status_code=status.HTTP_200_OK)
async def get_vehicle_location(vehicle_id: int, response: Response, user_info: authentication.authorize_passenger):
    entry = await db.get_vehicle_location(vehicle_id)
    if entry is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message" : "Error: Vehicle location is not available."}
    
    return {"message": "All Good.", "longitude": entry["longitude"], "latitude" : entry["latitude"]}

@app.post("/vehicle_location", status_code=status.HTTP_200_OK)
async def post_vehicle_location(vehicle_location_data: vehicle_location, response: Response, user_info : authentication.authorize_vehicle):
    vehicle_id = user_info["id"]
    latitude, longitude = vehicle_location_data.vehicle_id, vehicle_location_data.latitude, vehicle_location_data.longitude
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
async def put_vehicle_location(vehicle_location_data: vehicle_location, response: Response, user_info : authentication.authorize_vehicle):
    vehicle_id = user_info["id"]
    latitude, longitude = vehicle_location_data.latitude, vehicle_location_data.longitude
    result = await db.update_vehicle_location(vehicle_id, longitude=longitude, latitude=latitude)
    # False signifies that you tried to update the location of a vehicle whose location isn't in the db yet
    if result == "UPDATE 0":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message" : """Error: You have attempted to update the location of a vehicle who's location hasn't been added.
                            Maybe you mean to send a POST request?"""}
    else:
        return {"message": "All Good."}
    

@app.get("/route_details/{route_id}", status_code=status.HTTP_200_OK)
async def route_details(route_id: int, response:Response):
    if route_id not in app.state.routes:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Route not found"}
    return app.state.routes[route_id]["details"]


@app.get("/route/{requested_route_id}", status_code=status.HTTP_200_OK)
async def route(requested_route_id: int, response: Response):
    if requested_route_id not in app.state.routes:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Error: Route not found."}
    
    route_data = app.state.routes[requested_route_id]
    
    route_vehicles = await db.get_route_vehicles(requested_route_id)
    for vehicle in route_vehicles:
        del vehicle["latitude"]
        del vehicle["longitude"]
    route_data["vehicles"] = route_vehicles

    return {"message" : "All Good.", "route_data": route_data}



@app.get("/all_vehicles_location", status_code=status.HTTP_200_OK)
async def all_vehicles_location():
    vehicle_info = await db.get_all_vehicles_info()

    return {"message": "All good.",
            "content": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "status": vehicle["status"],
                            "id": vehicle["id"]
                        },
                        "geometry": {
                            "coordinates": [
                                vehicle["longitude"],
                                vehicle["latitude"]
                            ],
                            "type": "Point"
                        
                        }
                        }

                for vehicle in vehicle_info]
            }
        }


@app.get("/route_vehicles_eta/{route_id}", status_code=status.HTTP_200_OK)
async def route_vehicles_eta(route_id:int, response: Response,
                             pick_up_long:float, pick_up_lat:float): 
    # Load route
    if route_id not in app.state.routes:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Route not found."}
    route_geojson = app.state.routes[route_id]["line"]
    
    # Get route vehicles
    vehicles = await db.get_route_vehicles(route_id)
    if vehicles is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No vehicles available on the route with id '" + route_id  + "'.", 

                "available_vehicle" : {}}

    route = route_geojson["geometry"]["coordinates"]
    vehicles, av_vehicles_last_i = helper.filter_vehicles__pick_up((pick_up_long, pick_up_lat), vehicles, route)
    waypoints = await db.get_route_waypoints(route_id)
    for i in range(av_vehicles_last_i):
        vehicle = vehicles[i]

        vehicle_waypoints = helper.trim_waypoints_list(waypoints, 
                                                        (vehicle["longitude"], vehicle["latitude"]), 
                                                        (pick_up_long, pick_up_lat), route)
        vehicle["expected_time"] =  helper.get_time_estimation(vehicle_waypoints, MAPBOX_TOKEN , "driving")
        vehicle["passed"] = False

        del vehicle["longitude"]
        del vehicle["latitude"]
        del vehicle["projection_index"]

    for i in range(av_vehicles_last_i, len(vehicles)):
        vehicle = vehicles[i]
        vehicle["passed"] = True

        del vehicle["longitude"]
        del vehicle["latitude"]
        del vehicle["projection_index"]
    vehicles = vehicles[:av_vehicles_last_i][::-1] + vehicles[av_vehicles_last_i:]
    return {"message" : "All Good.", "vehicles" : vehicles}
    

@app.get("/vehicle/{vehicle_id}", status_code=status.HTTP_200_OK)
async def get_vehicle(vehicle_id: int):
    vehicle_details = await db.get_vehicle_details(vehicle_id)
    vehicle_route = app.state.routes[vehicle_details["route_id"]]
    vehicle_details["route_name"] = vehicle_route["details"]["route_name"]
    vehicle_details["remaining_route"] = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "LineString",
            "coordinates": helper.get_remaining_route(vehicle_route["line"]["geometry"]["coordinates"], vehicle_details["coordinates"])
        }
    }
    return {"message": "All Good", "content": vehicle_details}


@app.get("/time/driving", status_code=status.HTTP_200_OK)
async def vehicle_time(route_id:int, long1:float, lat1:float, long2:float, lat2:float, response: Response):
    # Load route
    if route_id not in app.state.routes:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Route not found."}
    route = app.state.routes[route_id]["line"]["geometry"]["coordinates"]
    waypoints = await db.get_route_waypoints(route_id)
    waypoints = helper.trim_waypoints_list(waypoints, (long1, lat1), (long2, lat2), route)
    return {"message": "All Good.", "time_estimation" : helper.get_time_estimation(waypoints, MAPBOX_TOKEN, "driving")}


@app.get("/time/walking", status_code=status.HTTP_200_OK)
async def vehicle_time(long1:float, lat1:float, long2:float, lat2:float, response: Response):
    return {"message": "All Good.", "time_estimation" : helper.get_time_estimation([(long1, lat1), (long2, lat2)], os.getenv("mapbox_token"), "walking")}

@app.get("/vehicle_eta/{vehicle_id}")
async def bus_eta(vehicle_id: int, pick_up_long:float, pick_up_lat:float):
    location = await db.get_vehicle_location(vehicle_id)
    v_long, v_lat = location["longitude"], location["latitude"]
    route_id = await db.get_vehicle_route_id(vehicle_id)
    route = app.state.routes[route_id]["line"]["geometry"]["coordinates"]
    route_waypoints = await db.get_route_waypoints(route_id)
    rem_waypoints = helper.trim_waypoints_list(route_waypoints, (v_long, v_lat), route_waypoints[-1][:2], route)
    passed = helper.before_on_route((pick_up_long, pick_up_lat), (v_long, v_lat), route)
    if passed:
        return {
            "message": "All good.",
            "content": {"passed": True}
        }
    else:
        return {
            "message": "All good.",
            "content":{
                "passed": False,
                "eta": helper.get_time_estimation(rem_waypoints, MAPBOX_TOKEN, "driving")
                }
        }



@app.get("/nearby_routes", status_code=status.HTTP_200_OK)
async def nearby_routes(long:float, lat:float, radius:float, 
                        long2: float | None=None, lat2: float|None = None, radius2: float|None=None):
    if long2 is not None and lat2 is not None and radius2 is not None:
        close_routes = await helper.get_nearby_routes_to_2_point(long, lat, radius, long2, lat2, radius2, app.state.routes.items())
    else:
        close_routes = await helper.get_nearby_routes_to_1_point(long, lat, radius, app.state.routes.items())
    return {"message": "All Good.", "routes": close_routes}

@app.get("/search_routes/{query}", status_code=status.HTTP_200_OK)
async def search_routes(query: str):
    route_ids = helper.search_routes(query, app.state.routes_search_data)
    res = []
    for route_id in route_ids:
        res.append({
            "route_id": route_id,
            "route_name": app.state.routes[route_id]["details"]["route_name"],
            "description": app.state.routes[route_id]["details"]["description"]
        })
    return {"message": "All good.", "routes": res}


@app.get("/search_vehicles/{query}", status_code=status.HTTP_200_OK)
async def search_vehicles(query: str):
    vehicles_search_info = await db.get_vehicles_search_info()
    
    vehicles_indices = helper.search_vehicles(query, vehicles_search_info)
    res = [vehicles_search_info[i] for i in vehicles_indices]

    return {"message": "All good.", "vehicles": res}



# feedback path operations
@app.post("/feedback/post", status_code=status.HTTP_200_OK)
async def post_feedback(passenger_id: int, vehicle_id: int, review: Review, response: Response):
    try:
        await db.add_feedback(passenger_id, vehicle_id, review)
        return {"message": "All Good."}
    except asyncpg.exceptions.UniqueViolationError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
                "message":
                """Error: You have attempted to add the feedback of a passenger whose feedback has
                already been added to this vehicle. Maybe you meant to send a PUT request?"""        
                }
    except asyncpg.exceptions.ForeignKeyViolationError as e:
        if "fk_vehicle" in str(e):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Error: You have attempted to add the feedback of a vehicle that doesn't exist."}
        elif "fk_passenger" in str(e):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Error: You have attempted to add the feedback of a passenger that doesn't exist."}
    except asyncpg.exceptions.CheckViolationError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Error: 'review' cannot be NULL. Please provide at least one of them."}
    
@app.put("/feedback/put/{passenger_id}/{vehicle_id}", status_code=status.HTTP_200_OK)
async def put_feedback(passenger_id: int, vehicle_id: int, review: Review, response: Response):
    try:
        result = await db.update_feedback(passenger_id, vehicle_id, review)
        if result == "UPDATE 0":
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message" : """Error: You have attempted to update the feedback of a passenger whose feedback hasn't been added to the vehicle yet.
                            Maybe you mean to send a POST request?"""}
        else:
            return {"message": "All Good."}
    except asyncpg.exceptions.CheckViolationError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Error: 'review' cannot be NULL. Maybe you meant a DELETE request?."}
    
@app.delete("/feedback/delete/passenger/{passenger_id}")
async def delete_passenger_feedbacks(passenger_id: int, response: Response):
    result = await db.remove_passenger_feedbacks(passenger_id)
    if result == "DELETE 0":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message" : """Error: You have attempted to delete a feedback that doesn't exist."""}
    else:
        return {"message": "All Good."}
    
@app.delete("/feedback/delete/vehicle/{vehicle_id}", status_code=status.HTTP_200_OK)
async def delete_vehicle_feedbacks( vehicle_id: int, response: Response):
    result = await db.remove_vehicle_feedbacks(vehicle_id)
    if result == "DELETE 0":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message" : """Error: You have attempted to delete a feedback that doesn't exist."""}
    else:
        return {"message": "All Good."}
    
@app.delete("/feedback/delete/{passenger_id}/{vehicle_id}", status_code=status.HTTP_200_OK)
async def delete_feedback(passenger_id: int, vehicle_id: int, response: Response):
    result = await db.remove_feedback(passenger_id, vehicle_id)
    if result == "DELETE 0":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message" : """Error: You have attempted to delete a feedback that doesn't exist."""}
    else:
        return {"message": "All Good."}


@app.get("/feedback/get/passenger/{passenger_id}", status_code=status.HTTP_200_OK)
async def get_passenger_feedbacks(passenger_id: int, response: Response):
    result = await helper.passenger_feedbacks(passenger_id, response)
    return result

@app.get("/feedback/get/vehicle/{vehicle_id}", status_code=status.HTTP_200_OK)
async def get_vehicle_feedbacks(vehicle_id: int, response: Response):
    result = await helper.vehicle_feedbacks(vehicle_id, response)
    return result

@app.get("/feedback/get/{passenger_id}/{vehicle_id}", status_code=status.HTTP_200_OK)
async def get_feedback(passenger_id: int, vehicle_id: int, response: Response):
    result = await helper.feedback(passenger_id, vehicle_id, response)
    return result

@app.get("/feedback/get", status_code=status.HTTP_200_OK)
async def get_all_feedbacks(response: Response):
    result = await helper.all_feedbacks(response)
    return result

@app.get("/station", status_code=status.HTTP_200_OK)
async def get_stations(response: Response):
    result = await db.get_stations()
    if (result is None) or not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "no stations."}
    else:
        return {"message": "All Good", "stations":result}