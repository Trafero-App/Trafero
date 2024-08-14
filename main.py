from fastapi import FastAPI, Response, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
import asyncpg
import os
from dotenv import load_dotenv, find_dotenv

from typing import Annotated, Literal
from validation_classes import Point, Account_Info, Account_DB_Entry, Passenger_Review, Review_DB_Entry

import helper
import authentication
from db_layer import db


load_dotenv(find_dotenv())
DB_URL = os.getenv("db_url")
MAPBOX_TOKEN = os.getenv("mapbox_token")
VEHICLE_TO_ROUTE_THRESHOLD = int(os.getenv("vehicle_to_route_threshold"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Open connection to database when app starts up
    await db.connect(DB_URL)

    # Load all routes for efficient access later on
    app.state.routes = db.routes
    app.state.routes_search_data = db.routes_search_data
    yield
    
    # Close the connection to the db when the app shuts down
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
    allow_credentials=True, # allow credentials to be sent
    allow_methods=["*"], # allow POST, GET, PUT ... `*` is "all"
    allow_headers=["*"]

)



@app.post("/signup", status_code=status.HTTP_200_OK)
async def signup(account_data: Account_Info):
    """Validate user data and add it to database.

    Parameters:
    - account_data: Account data of user signing up

    Returns:
    - Message indicating the sign-up process went smoothly

    Raises:
    - HTTPException: If username is already in use. (status code: 409)
    - HTTPException: If phone number is already in use. (status code: 409)
    - HTTPException: If email is already in use. (status code: 409)
    - HTTPException: If `account_data` is not in the correct format (status code: 422)
    """
    account_type = account_data.account_type
    username_av = await db.check_username_available(account_data.username, account_type)
    phone_num_av = await db.check_phone_number_available(account_data.phone_number, account_type)
    email_av = await db.check_email_available(account_data.email, account_data.account_type)
    if not username_av:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={"error_code": "USERNAME_ALREADY_USED",
                                    "msg": "The username you attempted to sign-up with is already used by another user."})
    
    if not phone_num_av:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={"error_code": "PHONE_NUM_ALREADY_USED",
                                    "msg":"The phone number you attempted to sign-up with is already used by another user."
                                    }
                            )
    
    if not email_av:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={"error_code": "PHONE_NUM_ALREADY_USED",
                                    "msg":"The email you attempted to sign-up with is already used by another user."
                                    }
                            )

    password_hash = authentication.hash_password(account_data.password)
    await db.add_account(Account_DB_Entry(**account_data.model_dump(exclude={"password"}), password_hash=password_hash))
    return {"message": "Account was signed up successfully."}
    

@app.post("/login/{account_type}", status_code=status.HTTP_200_OK)
async def login(account_type: Literal["passenger", "vehicle"], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Validate user credentials and provide authentication token

    Parameters:
    - account_type: specifies if the user is attempting to log in
      as a passenger or as a vehicle
    - from_data: data containing user credentials (username and password)

    Returns:
    - Authentication token

    Raises:
    - HTTPException: If credentials are invalid (status code: 401)
    """
    user = await authentication.check_user_credentials(form_data.username, form_data.password, account_type)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error_code": "INVALID_CREDENTIALS",
                                                                              "msg": "The entered credentials are invalid"})
    token_data = {"sub": user["username"], "type": account_type}
    access_token = authentication.create_access_token(
        token_data=token_data
    )
    return {"message": "Token generated successfully.", "token": {"access_token": access_token, "token_type": "bearer"}}


@app.get("/vehicle_location/{vehicle_id}", status_code=status.HTTP_200_OK)
async def get_vehicle_location(vehicle_id: int):
    """Get the location of the vehicle having id `vehicle_id`

    Parameters:
    - vehicle_id: id of the vehicle whose location is needed

    Returns:
    - [long, lat] representing the vehicle's coordinates

    Raises:
    - HTTPException: If the entered vehicle id doesn't correspond 
      to a valid vehicle in the database (status code: 404)

    """
    entry = await db.get_vehicle_location(vehicle_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error_code": "INVALID_VEHICLE_ID", "msg": f"'{vehicle_id}' isn't a valid vehicle id"})
    
    return {"message": "Coordinates found successfully.", "coordinates":[entry["longitude"], entry["latitude"]]}

@app.post("/vehicle_location", status_code=status.HTTP_200_OK)
async def post_vehicle_location(vehicle_location_data: Point, user_info : authentication.authorize_vehicle):
    """Adds the location of an existing vehicle to the database

    Parameters:
    - vehicle_location_data: A `Point` representing the vehicle's location
    - user_info: user information extracted from the authentication token

    Returns:
    - Message indicating the location was succesfully updated
    
    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If the request doesn't include a valid vehicle account
      access token (status code: 422)
    - HTTPException: If the location of the vehicle has already been added. (status code: 400)
    - HTTPException: If the vehicle id is invalid (status code: 400)

    Notes:
    - Only requests with tokens corresponding to vehicle accounts may 
    send this request.
    - Only use this POST request to add the location of a vehicle when
      its location hasn't been added already. To update the location
      of a vehicle, send a PUT request to `/vehicle_location`
    """
    vehicle_id = user_info["id"]
    latitude, longitude = vehicle_location_data.latitude, vehicle_location_data.longitude
    try:
        await db.add_vehicle_location(vehicle_id, longitude=longitude, latitude=latitude)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"error_code": "LOCATION_ALREADY_ADDED",
                                    "msg": "Your location has already been added. Maybe you meant to send a PUT request?"})
    except asyncpg.exceptions.ForeignKeyViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"error_code": "INVALID_VEHICLE_ID",
                                    "msg": "The vehicle id used is invalid.Try to generate another token."})
    return {"message": "All Good."}


@app.put("/vehicle_location", status_code=status.HTTP_200_OK)
async def put_vehicle_location(vehicle_location_data: Point, response: Response, user_info : authentication.authorize_vehicle):
    vehicle_id = user_info["id"]
    latitude, longitude = vehicle_location_data.latitude, vehicle_location_data.longitude
    success = await db.update_vehicle_location(vehicle_id, longitude=longitude, latitude=latitude)
    # False signifies that you tried to update the location of a vehicle whose location isn't in the db yet
    if not success:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message" : """Error: You have attempted to update the location of a vehicle who's location hasn't been added.
                            Maybe you mean to send a POST request?"""}
    else:
        
        route_id = await db.get_vehicle_route_id(vehicle_id)
        route = app.state.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]
        if helper.off_track((longitude, latitude), route, VEHICLE_TO_ROUTE_THRESHOLD):
            await db.update_status(vehicle_id, "unknown")
            return {"message": "status set to unavailable. You are too far from the route."}
        else:
            return {"message": "All Good. Status set to active."}


@app.put("/vehicle_status", status_code=status.HTTP_200_OK)
async def put_vehicle_status(vehicle_id: int, new_status: Literal["active", "waiting", "unavailable", "inactive", "unknown"],
                             response: Response):
    success = await db.update_status(vehicle_id, new_status)
    if success: return {"message": "All good."}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No such vehicle"}


@app.put("/active_route", status_code=status.HTTP_200_OK)
async def change_active_route (new_active_route: int, response: Response, user_info : authentication.authorize_vehicle):
    vehicle_id = user_info["id"]
    vehicle_routes = await db.get_vehicle_routes(vehicle_id)
    if new_active_route not in vehicle_routes:
        response.status = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Invalid route id"}
    else:
        await db.change_active_route(vehicle_id, new_active_route)
        return {"message": "All good."}

@app.post("/vehicle_routes/add", status_code=status.HTTP_200_OK)
async def add_vehicle_route(new_route_id: int, response: Response, user_info: authentication.authorize_vehicle):
    vehicle_id = user_info["id"]
    try:
        await db.add_route(vehicle_id, new_route_id)
    except asyncpg.exceptions.ForeignKeyViolationError:
        return {"message": "Route doesn't exist."}
    except asyncpg.exceptions.UniqueViolationError:
        return {"message": f"Route with id '{new_route_id}' is already added to the route list of vehicle with id'{vehicle_id}'"}
    return {"message": "All good."}


@app.delete("/vehicle_routes/delete", status_code=status.HTTP_200_OK)
async def delete_vehicle_route(route_id: int, response: Response, user_info: authentication.authorize_vehicle):
    deleted = await db.delete_vehicle_route(user_info["id"], route_id)
    if not deleted:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Route isn't in the list"}
    else:
        return {"message": "All good."}


@app.get("/route_details/{route_id}", status_code=status.HTTP_200_OK)
async def route_details(route_id: int, response:Response):
    if route_id not in app.state.routes:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Error: Route not found."}
    
    route_data = helper.flatten_route_data(app.state.routes[route_id])

    return {"message" : "All Good.", "route_data": route_data}



@app.get("/route/{route_id}", status_code=status.HTTP_200_OK)
async def route(route_id: int, response: Response):
    if route_id not in app.state.routes:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Error: Route not found."}
    
    route_data = await helper.get_route_data(int(route_id), num='')
    return {"message" : "All Good.", "route_data": route_data}



@app.get("/all_vehicles_location", status_code=status.HTTP_200_OK)
async def get_all_vehicles_location():
    res = await helper.all_vehicles_info()
    return {"message": "All good.", "content": res}



@app.get("/route_vehicles_eta/{route_id}", status_code=status.HTTP_200_OK)
async def route_vehicles_eta(route_id:int, response: Response,
                             pick_up_long:float, pick_up_lat:float): 
    # Load route
    if route_id not in app.state.routes:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Route not found."}
    
    # Get route vehicles
    vehicles = await db.get_route_vehicles(route_id)
    if vehicles is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No vehicles available on the route with id '" + route_id  + "'.", 

                "available_vehicle" : {}}

    vehicles_eta = await helper.get_route_vehicles_eta((pick_up_long, pick_up_lat), vehicles, route_id, MAPBOX_TOKEN)
    return {"message" : "All Good.", "vehicles" : vehicles_eta}
    

@app.get("/vehicle/{vehicle_id}", status_code=status.HTTP_200_OK)
async def get_vehicle(vehicle_id: int, response: Response, user_info: authentication.authorize_anyone):
    if user_info is not None and user_info["type"] == "passenger":
        passenger_id = user_info.get("id")
    else: passenger_id = None
    vehicle_details = await db.get_vehicle_details(vehicle_id)
    if vehicle_details is None:
        response.status = status.HTTP_404_NOT_FOUND
        return {"message": "vehicle not found"}
    vehicle_route = app.state.routes[vehicle_details["route_id"]]
    vehicle_details["route_name"] = vehicle_route["details"]["route_name"]
    if passenger_id is not None:
        vehicle_details["user_choice"] = (await db.get_passenger_reaction(passenger_id, vehicle_id))["reaction"]
    else:
        vehicle_details["user_choice"] = None

    vehicle_details["remaining_route"] = helper.get_remaining_route(vehicle_details["route_id"], vehicle_details["coordinates"])

    return {"message": "All Good", "content": vehicle_details}


@app.get("/time/driving", status_code=status.HTTP_200_OK)
async def vehicle_time(route_id:int, long1:float, lat1:float, long2:float, lat2:float, response: Response):
    # Load route
    if route_id not in app.state.routes:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Route not found."}
    waypoints = await db.get_route_waypoints(route_id)
    waypoints = helper.trim_waypoints_list(waypoints, (long1, lat1), (long2, lat2), route_id)
    return {"message": "All Good.", "time_estimation" : helper.get_time_estimation(waypoints, MAPBOX_TOKEN, "driving")}


@app.get("/time/walking", status_code=status.HTTP_200_OK)
async def vehicle_time(long1:float, lat1:float, long2:float, lat2:float, response: Response):
    return {"message": "All Good.", "time_estimation" : helper.get_time_estimation([(long1, lat1), (long2, lat2)], os.getenv("mapbox_token"), "walking")}

@app.get("/vehicle_eta/{vehicle_id}")
async def vehicle_eta(vehicle_id: int, pick_up_long:float, pick_up_lat:float):
    res = await helper.get_vehicle_time_estimation(vehicle_id, (pick_up_long, pick_up_lat), MAPBOX_TOKEN)
    return { "message": "All good.", "content": res}


@app.get("/nearby_routes", status_code=status.HTTP_200_OK)
async def nearby_routes(long:float, lat:float, radius:float, 
                        long2: float | None=None, lat2: float|None = None, radius2: float|None=None):
    if long2 is not None and lat2 is not None and radius2 is not None:
        close_routes = await helper.get_nearby_routes(long, lat, radius, long2, lat2, radius2, MAPBOX_TOKEN)
    else:
        close_routes = await helper.get_nearby_routes_to_1_point(long, lat, radius)
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
    res = [{"id": vehicles_search_info[i][0], "license_plate": vehicles_search_info[i][1],
            "status": vehicles_search_info[i][2]} for i in vehicles_indices]

    return {"message": "All good.", "vehicles": res}



# feedback path operations
@app.post("/feedback", status_code=status.HTTP_200_OK)
async def post_feedback(review: Passenger_Review, response: Response, user_info : authentication.authorize_passenger):
    passenger_id = user_info["id"]
    review_entry = Review_DB_Entry(**review.model_dump(), passenger_id=passenger_id)
    try:
        print('x)')
        await db.add_feedback(review_entry)
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

@app.put("/feedback", status_code=status.HTTP_200_OK)
async def put_feedback(review: Passenger_Review, response: Response, user_info: authentication.authorize_passenger):
    
    passenger_id = user_info["id"]
    review_entry = Review_DB_Entry(**review.model_dump(), passenger_id=passenger_id)
    try:
        success = await db.update_feedback(review_entry)
        if not success:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Feedback cannot be updated (it doesn't exist)"}
        return {"message": "All Good."}
    except asyncpg.exceptions.ForeignKeyViolationError as e:
        if "fk_vehicle" in str(e):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Error: Invalid vehicle id"}
        elif "fk_passenger" in str(e):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Error: Invalid passenger id"}
        
    return {"message": "All good."}


@app.get("/my_reaction/{vehicle_id}", status_code=status.HTTP_200_OK)
async def get_my_reaction(vehicle_id: int, response: Response, user_info: authentication.authorize_passenger):
    passenger_id = user_info["id"]
    return await db.get_passenger_reaction(passenger_id, vehicle_id)

@app.get("/feedback/{vehicle_id}", status_code=status.HTTP_200_OK)
async def get_vehicle_feedback(vehicle_id: int, response: Response):
    return await db.get_vehicle_feedback(vehicle_id)

@app.delete("/feedback/{vehicle_id}", status_code=status.HTTP_200_OK)
async def delete_vehicle_feedback(vehicle_id: int, response: Response, user_info: authentication.authorize_passenger):
    passenger_id = user_info["id"]
    success = await db.delete_feedback(vehicle_id, passenger_id)
    if success: return {"message": "All good."}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Entry doesn't exist"}


@app.get("/station", status_code=status.HTTP_200_OK)
async def get_stations(response: Response):
    result = await db.get_stations()
    if (result is None) or not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "no stations."}
    else:
        features = []
        for stop in result:
            properties = helper.flatten_route_data(app.state.routes[stop["route_id"]])
            del properties["route_name"]
            del properties["description"]
            del properties["company_name"]
            del properties["phone_number"]
            del properties["distance"]
            del properties["estimated_travel_time"]
            del properties["route_type"]
            properties["stop_name"] = stop["station_name"]
            feature = {
                "type": "Feature",
                "properties": properties,
                "geometry": {
                    "coordinates": [
                        stop["longitude"],
                        stop["latitude"]
                    ],
                    "type": "Point"
                }
            }
            features.append(feature)
             
        return {"message": "All Good", "content":{
            "type": "FeatureCollection",
            "features": features 
        }}
    
@app.get("/Jtest/{route_id}", status_code=status.HTTP_200_OK)
async def testt(route_id):
    res = await helper.get_route_data(int(route_id), num='')
    return res