"""
main.py

This module handles direct requests from the front end, processes them,
and provides results based on imported functions from helper files.

Functions:
- Accounts-related functions
- Routes and Stations-related functions
- Vehicles-related functions
- Feedback-related functions
- Search-related functions
"""

from fastapi import FastAPI, Response, status, Depends, HTTPException, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncpg
import os
from dotenv import load_dotenv, find_dotenv

from typing import Annotated, Literal, List
from validation import is_valid_license_plate, is_valid_email, is_valid_phone_number, Account_Info, \
    Point, Account_DB_Entry, Passenger_Review, Review_DB_Entry, Saved_Location, Saved_Vehicle

import helper
import authentication
from database import db

load_dotenv(find_dotenv())
DB_URL = os.getenv("db_url")
MAPBOX_TOKEN = os.getenv("mapbox_token")
VEHICLE_TO_ROUTE_THRESHOLD = int(os.getenv("vehicle_to_route_threshold"))
DRIVING_LICENSES_PATH = os.getenv("driving_licenses_path")
VEHICLE_REGISTRATIONS_PATH = os.getenv("vehicle_registrations_path")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Open connection to database when app starts up
    await db.connect(DB_URL)

    # Load all routes for efficient access later on
    app.state.routes = db.routes
    app.state.routes_search_data = db.routes_search_data
    
    # p = (35.483226, 33.882462)

    # print(helper.project_point_on_route(p, 2), helper.project_point_on_route(p, 13))
    # print(helper.project_point_on_route(p, 2, True), helper.project_point_on_route(p, 13, True))
    # print(db.routes[2]["line"]["features"][0]["geometry"]["coordinates"][693])
    # print(db.routes[13]["line"]["features"][0]["geometry"]["coordinates"][171])
    yield
    # (681, 6.6235988991033565) (186, 23.000936233861424)
    
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
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/signup", status_code=status.HTTP_200_OK)
async def signup(request: Request):
    """Validate user data and add it to database.

    Parameters:
    - request: data of the received request

    Returns:
    - Message indicating the sign-up process went smoothly

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If email or phone number is already in use. (status code: 409)
    """
    form_data = dict(await request.form())
    account_data: Account_Info = helper.get_account_info_from_form(form_data)
    account_type = account_data.account_type

    if account_data.phone_number is not None:
        is_available_phone_number = await db.check_phone_number_available(account_data.phone_number, account_type)
        if not is_available_phone_number:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"error_code": "PHONE_NUM_UNAVAILABLE",
                                        "msg":"The phone number you attempted to sign-up with is already used by another user."
                                        }
                                )
    
    if account_data.email is not None:
        is_available_email = await db.check_email_available(account_data.email, account_type)
        if not is_available_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"error_code": "EMAIL_UNAVAILABLE",
                                        "msg":"The email you attempted to sign-up with is already used by another user."
                                        }
                                )
 
    if account_type == "driver":
        drivers_license_file, vehicle_registration_file = helper.get_files(form_data)
        if drivers_license_file is None or vehicle_registration_file is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                                detail={"error_code": "MISSING_FILES",
                                        "msg": "Please provide both a drivers license and a vehicle registration"})

    password_hash = authentication.hash_password(account_data.password)
    user_id = await db.add_account(Account_DB_Entry(**account_data.model_dump(exclude={"password"}),
                                                    password_hash=password_hash))
    
    if account_type == "driver":
        vehicle_id = await db.get_driver_vehicle_id(user_id)
        helper.save_files(form_data, f"{DRIVING_LICENSES_PATH}/{user_id}.pdf", f"{VEHICLE_REGISTRATIONS_PATH}/{vehicle_id}.pdf")

    if account_type == "driver":
        vehicle_id = await db.get_driver_vehicle_id(user_id)
        await db.add_vehicle_location(vehicle_id, None, None)
    
    access_token = authentication.create_access_token(user_id, account_type)
    return {"message": "Account was signed up successfully.", "token": {"access_token": access_token, "token_type": "bearer"}}
    

@app.get("/check_email", status_code=status.HTTP_200_OK)
async def check_email(email: str):
    """Check if email has proper form and is unused"""
    has_proper_form = is_valid_email(email)
    is_unused = await db.check_email_available(email)
    return {"message": "Validating email complete.", "is_valid": has_proper_form and is_unused}



@app.get("/check_phone_number", status_code=status.HTTP_200_OK)
async def check_phone_number(phone_number: str):
    """Check if phone number has proper form and is unused"""
    has_proper_form = is_valid_phone_number(phone_number)
    is_unused = await db.check_phone_number_available(phone_number)
    return {"message": "Validating email complete.", "is_valid": has_proper_form and is_unused}


@app.get("/check_license_plate", status_code=status.HTTP_200_OK)
async def check_phone_number(license_plate: str):
    """Check if license plate has proper form and is unused"""
    has_proper_form = is_valid_license_plate(license_plate)
    is_unused = await db.check_license_plate_available(license_plate)
    return {"message": "Validating license plate complete.", "is_valid": has_proper_form and is_unused}


@app.post("/login/{account_type}", status_code=status.HTTP_200_OK)
async def login(account_type: Literal["passenger", "driver"], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Validate user credentials and provide authentication token

    Parameters:
    - account_type: specifies if the user is attempting to log in
      as a passenger or as a driver
    - form_data: data containing user credentials (username and password)

    Returns:
    - Authentication token

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If credentials are invalid (status code: 401)
    """
    identifier = form_data.username
    if is_valid_phone_number(identifier): login_method = "phone_number"
    else: login_method = "email"

    user = await authentication.check_user_credentials(form_data.username, form_data.password, account_type, login_method)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error_code": "INVALID_CREDENTIALS",
                                                                              "msg": "The entered credentials are invalid"})

    access_token = authentication.create_access_token(user["id"], account_type)
    return {"message": "Token generated successfully.", "token": {"access_token": access_token, "token_type": "bearer"}}



@app.get("/account_info")
async def get_account_info(user_info: authentication.authorize_any_account):
    """Give account info"""
    del user_info["password_hash"]
    if user_info["account_type"] == "driver": # user is a driver
        user_info["route_list"] = [{"route_id": route_id,
                                    "route_name": db.routes[route_id]["details"]["route_name"],
                                    "description": db.routes[route_id]["details"]["description"],
                                    "line": db.routes[route_id]["line"]
                                    } for route_id in user_info["route_list"]]
        
    user_info["saved_routes"] = await db.get_user_saved_routes(user_info["id"], user_info["account_type"])
    user_info["saved_vehicles"] = await db.get_user_saved_vehicles(user_info["id"], user_info["account_type"])
    user_info["saved_locations"] = await db.get_user_saved_locations(user_info["id"], user_info["account_type"])
    return user_info

@app.put("/saved_routes")
async def set_account_saved_routes(saved_routes: Annotated[List[int], Body(embed=True)], user_info: authentication.authorize_any_account):
    """Set user's saved routes"""
    await db.set_user_saved_routes(user_info["id"], saved_routes, user_info["account_type"])
    return {"message": "Successfully updated"}

@app.put("/saved_vehicles")
async def set_account_saved_vehicles(saved_vehicles: Annotated[List[Saved_Vehicle], Body(embed=True)], user_info: authentication.authorize_any_account):
    """Set user's saved vehicles"""
    await db.set_user_saved_vehicles(user_info["id"], saved_vehicles, user_info["account_type"])
    return {"message": "Successfully updated"}

@app.put("/saved_locations")
async def set_account_saved_locations(saved_locations: Annotated[List[Saved_Location], Body(embed=True)], user_info: authentication.authorize_any_account):
    """Set user's saved locations"""
    await db.set_user_saved_locations(user_info["id"], saved_locations, user_info["account_type"])
    return {"message": "Successfully updated"}



@app.put("/vehicle_location", status_code=status.HTTP_200_OK)
async def put_vehicle_location(vehicle_location_data: Point, user_info : authentication.authorize_driver):
    """Update the location of an existing vehicle in the database

    Parameters:
    - vehicle_location_data: A `Point` representing the vehicle's location
    - user_info: user information extracted from the authentication token

    Returns:
    - Message indicating the location was succesfully added

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If the request doesn't include a valid vehicle account
      unexpired access token (status code: 401)
    - HTTPException: If the location of the vehicle has not been added yet (status code: 400)
    - HTTPException: If the vehicle id is invalid (status code: 400)

    Notes:
    - Only requests with tokens corresponding to vehicle accounts may 
      send this request.
    - Only use this PUT request to update the location of a vehicle when
      its location has been added already. To add the location of a vehicle,
      send a POST request to `/vehicle_location`
    """
    vehicle_id = await db.get_driver_vehicle_id(user_info["id"])
    latitude, longitude = vehicle_location_data.latitude, vehicle_location_data.longitude
    success = await db.update_vehicle_location(vehicle_id, longitude=longitude, latitude=latitude)
    # False signifies that you tried to update the location of a vehicle whose location isn't in the db yet
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail={"error_code": "LOCATION_NOT_ADDED_PREVIOUSLY",
                                    "msg": "Your location has not been added previously. Maybe you meant to send a POST request?"})
    else:   
        route_id = await db.get_vehicle_route_id(vehicle_id)
        if helper.off_track((longitude, latitude), route_id, VEHICLE_TO_ROUTE_THRESHOLD):
            await db.update_status(vehicle_id, "unknown")
            return {"message": "Location succesfully updated. Status set to unknown: you are too far from your route."}
        else:
            return {"message": "Location succesfully updated."}



@app.put("/vehicle_status", status_code=status.HTTP_200_OK)
async def put_vehicle_status(new_status: Literal["active", "waiting", "unavailable", "inactive", "unknown"], user_info: authentication.authorize_driver): # to be changed
    """Update vehicle status

    Parameters:
    - new_status: the status the vehicle should take on
    - user_info: user information extracted from the authentication token

    Returns:
    - Message indicating the status was successfully updated

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If no vehicle with the given id is found (status code: 404)
    """
    
    vehicle_id = await db.get_driver_vehicle_id(user_info["id"])
    success = await db.update_status(vehicle_id, new_status)
    if success:
        return {"message": "Status updated successfully."}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail={"error_code": "INVALID_VEHICLE_ID",
                              "msg": "The given vehicle id is invalid"})



@app.put("/active_route", status_code=status.HTTP_200_OK)
async def change_active_route (new_active_route: int, user_info : authentication.authorize_driver):
    """Update the active route of a certain vehicle


    Parameters:
    - new_active_route: The id of the route that the vehicle is
      to take on as its active route.
    - user_info: user information extracted from the authentication token

    Returns:
    - Message indicating the vehicle's active route was successfully updated

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If the request doesn't include a valid vehicle account
      unexpired access token (status code: 401)
    - HTTPException: if the given route id is not one of the vehicle's
      routes (status code: 406)
    - HTTPException: If no vehicle with the given id is found (status code: 404)
    """
    vehicle_id = await db.get_driver_vehicle_id(user_info["id"])
    vehicle_routes = await db.get_vehicle_routes(vehicle_id)
    if new_active_route not in vehicle_routes:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail={"error_code": "ROUTE_NOT_VALID_FOR_THIS_VEHICLE"})
    success = await db.change_active_route(vehicle_id, new_active_route)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error_code": "INVALID_VEHICLE_ID",
                                    "msg": "The vehicle id used is invalid. Try to generate another token."})

    
    return {"message": f"Changed your active route to the route with id '{new_active_route}'"}



@app.post("/vehicle_routes", status_code=status.HTTP_200_OK)
async def add_vehicle_route(new_routes_ids: Annotated[List[int], Body(embed=True)], user_info: authentication.authorize_driver):
    """Updates the routes of a vehicle
    
    Parameters:
    - new_routes: list of ids of the routes of the vehicle
    - user_info: user information extracted from the authentication token

    Returns:
    - Message indicating the vehicle's routes where replaced successfully

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If the request doesn't include a valid vehicle account
      unexpired access token (status code: 401)
    - HTTPException: If any of the given route ids is invalid (status code: 404)

    """
    vehicle_id = await db.get_driver_vehicle_id(user_info["id"])
    try:
        await db.set_route(vehicle_id, new_routes_ids)
    except asyncpg.exceptions.ForeignKeyViolationError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error_code": "INVALID_ROUTE_ID",
                                    "msg": "One of the route ids given is invalid"})
    return {"message": f"Successfully replaced your route_list with {new_routes_ids}"}



@app.get("/route_details/{route_id}", status_code=status.HTTP_200_OK)
async def route_details(route_id: int):
    """Get details of a specific route

    Parameters:
    - route_id

    Returns:
    - Details of the requested route

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If the route id is invalid (status code: 404)
    """
    if route_id not in app.state.routes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error_code": "INVALID_ROUTE_ID",
                                    "msg": "The given route id is invalid"})
    
    route_data = helper.flatten_route_data(app.state.routes[route_id])

    return {"message" : f"Successfully collected route details",
            "route_data": route_data}



@app.get("/route/{route_id}", status_code=status.HTTP_200_OK)
async def route(route_id: int):
    """Get some information and current vehicles of a specific route 

    Parameters:
    - route_id

    Returns:
    - Requested info

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: if the given route_id is invalid (status_code: 404)
    """
    if route_id not in app.state.routes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error_code": "INVALID_ROUTE_ID",
                                    "msg": "The given route id is invalid"})
    
    route_data = await helper.get_route_details(int(route_id), num='')
    return {"message" : "Successfully collected route data", "route_data": route_data}



@app.get("/all_vehicles_location", status_code=status.HTTP_200_OK)
async def get_all_vehicles_location():
    """Get the location and status of all vehicles"""
    res = await helper.all_vehicles_info()
    return {"message": "All good.", "content": res}



@app.get("/route_vehicles_eta/{route_id}", status_code=status.HTTP_200_OK)
async def route_vehicles_eta(route_id:int, pick_up_long:float, pick_up_lat:float):
    """Get the etas of all vehicles on a specific route to
    a specific destination

    Parameters:
    - route_id
    - [pick_up_long, pick_up_lat]: coordinates of the destination

    Returns:
    - The eta of every vehicle to the destination. If the vehicle,
      already passed
    """
    # Load route
    if route_id not in app.state.routes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error_code": "INVALID_ROUTE_ID",
                                    "msg": "The given route id is invalid"})
    
    # Get route vehicles
    vehicles = await db.get_route_vehicles(route_id)
    if vehicles is None: vehicles = []

    # vehicles_eta = await helper.get_route_vehicles_eta((pick_up_long, pick_up_lat), vehicles, route_id, MAPBOX_TOKEN)
    pickup = (pick_up_long, pick_up_lat)
    vehicles_eta = await helper.get_route_vehicles_arrival_status(pickup, vehicles, route_id, MAPBOX_TOKEN)
    return {"message" : "All Good.", "vehicles" : vehicles_eta}
    


@app.get("/vehicle/{vehicle_id}", status_code=status.HTTP_200_OK)
async def get_vehicle(vehicle_id: int, user_info: authentication.authorize_anyone):
    """Get information about a specific vehicle

    Parameters:
    - vehicle_id

    Returns:
    - Details of the vehicle with id `vehicle_id`

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: if the given route_id is invalid (status_code: 404)
    """
    if user_info is not None and user_info["account_type"] == "passenger":
        passenger_id = user_info.get("id")
    else: passenger_id = None
    vehicle_details = await db.get_vehicle_details(vehicle_id)
    if vehicle_details is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail={"error_code": "INVALID_VEHICLE_ID",
                              "msg": "The given vehicle id is invalid"})
    vehicle_route = app.state.routes[vehicle_details["route_id"]]
    vehicle_details["route_name"] = vehicle_route["details"]["route_name"]
    if passenger_id is not None:
        vehicle_details["user_choice"] = (await db.get_passenger_reaction(passenger_id, vehicle_id))["reaction"]
    else:
        vehicle_details["user_choice"] = None

    vehicle_details["remaining_route"] = helper.get_remaining_route(vehicle_details["route_id"], vehicle_details["coordinates"])

    return {"message": "All Good", "content": vehicle_details}


@app.get("/vehicle_eta/{vehicle_id}")
async def vehicle_eta(vehicle_id: int, pick_up_long:float, pick_up_lat:float):
    res = await helper.get_arrival_status(vehicle_id, (pick_up_long, pick_up_lat), MAPBOX_TOKEN)
    return { "message": "All good.", "content": res}



@app.get("/nearby_routes", status_code=status.HTTP_200_OK)
async def nearby_routes(long:float, lat:float, radius:float, 
                        long2: float | None=None, lat2: float|None = None, radius2: float|None=None):
    """Get the eta of all busses on a specific route to
    a specific destination

    Parameters:
    - route_id: the id of the route whose vehicle etas are requested
    - [pick_up_long, pick_up_lat]: coordinates of the destination

    Returns:
    - The eta of every vehicle to the destination. If the vehicle,
      already
    """
    if long2 is not None and lat2 is not None and radius2 is not None:
        close_routes = await helper.all_nearby_routes_2_points(long, lat, min(radius, 1500), long2, lat2, min(radius2, 1500), MAPBOX_TOKEN)
        if close_routes == []:
            close_routes = await helper.all_nearby_routes_2_points(long, lat, min(radius * 2, 1500), long2, lat2, min(radius2 * 2, 1500), MAPBOX_TOKEN)
    else:
        close_routes = await helper.nearby_routes_to_a_point_formated(long, lat, min(radius, 1500))
        if close_routes == []:
            close_routes = await helper.nearby_routes_to_a_point_formated(long, lat, min(radius * 2, 1500))
        
    return {"message": "All Good.", "routes": close_routes}



@app.get("/search_routes/{query}", status_code=status.HTTP_200_OK)
async def search_routes(query: str):
    """Get routes based on a query

    Parameters:
    - Query: the word the user is searching for

    Returns:
    - All routes related to the query
    """
    route_ids = helper.search_routes(query)
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
    """Get vehicles based on a search query

    Parameters:
    - Query: license plate 

    Returns:
    - Vehicle that holds the license plate
    """
    vehicles_search_info = await db.get_vehicles_search_info()
    
    vehicles_indices = helper.search_vehicles(query, vehicles_search_info)
    res = [{"id": vehicles_search_info[i][0], "license_plate": vehicles_search_info[i][1],
            "status": vehicles_search_info[i][2]} for i in vehicles_indices]

    return {"message": "All good.", "vehicles": res}



# feedback path operations
@app.post("/feedback", status_code=status.HTTP_200_OK)
async def post_feedback(review: Passenger_Review, user_info : authentication.authorize_passenger):
    """Add the feedback of a passenger on a vehicle

    Parameters:
    - Passenger_Review: conatins the review details + vehicle_id
    - user_info: user information extracted from the authentication token

    Returns:
    - Message indicating the passenger's review was successfully added

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If the request doesn't include a valid passenger account
      unexpired access token (status code: 401)
    - HTTPException: if the given vehicle_id doesn't exist (status_code: 404)
    - HTTPException: if the passenger already added a previous feedback to this vehicle (status_code: 409)
    """
    passenger_id = user_info["id"]
    review_entry = Review_DB_Entry(**review.model_dump(), passenger_id=passenger_id)
    try:
        await db.add_feedback(review_entry)
        return {"message": "All Good."}
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_409_BAD_REQUEST,
                            detail={"error_code": "FEEDBACK_ALREADY_ADDED",
                                    "msg": "The feedback of this user to this vehicle has already been added"})
    
    except asyncpg.exceptions.ForeignKeyViolationError as e:
        if "fk_vehicle" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail={"error_code": "INVALID_VEHICLE_ID", "msg": "The given vehicle id is invalid"})
    
    return {"message": "Feedback successfully added"}



@app.put("/feedback", status_code=status.HTTP_200_OK)
async def put_feedback(review: Passenger_Review, user_info: authentication.authorize_passenger):
    """Update the feedback of a passenger on a vehicle

    Parameters:
    - Passenger_Review: conatins the review details + vehicle_id
    - user_info: user information extracted from the authentication token

    Returns:
    - Message indicating the passenger's review was successfully updated

    Raises:
    - HTTPException: if the given vehicle_id is invalid (status_code: 404)
    - HTTPException: if the passenger didn't add a previous feedback to this vehicle (status_code: 404)
    """
    
    passenger_id = user_info["id"]
    review_entry = Review_DB_Entry(**review.model_dump(), passenger_id=passenger_id)
    try:
        success = await db.update_feedback(review_entry)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST,
                                detail={"error_code": "FEEDBACK_NOT_FOUND",
                                        "msg": "This user didnt submit a feedback to this vehicle."})
    except asyncpg.exceptions.ForeignKeyViolationError as e:
        if "fk_vehicle" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail={"error_code": "INVALID_VEHICLE_ID",
                                "msg": "The given vehicle id is invalid"})
        
    return {"message": "Feedback successfully updated"}



@app.delete("/feedback/{vehicle_id}", status_code=status.HTTP_200_OK)
async def delete_vehicle_feedback(vehicle_id: int, user_info: authentication.authorize_passenger):
    """Delete feedback of a passenger on a vehicle

    Parameters:
    - vehicle_id
    - user_info: user information extracted from the authentication token

    Returns:
    - Message indicating the passenger's review was successfully added

    Raises:
    - HTTPException: if feedback doesn't exist (status_code: 404)
    """
    passenger_id = user_info["id"]
    success = await db.delete_feedback(passenger_id, vehicle_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error_code": "FEEDBACK_NOT_FOUND",
                                    "msg": "Feedback doesn't exist"})
    return {"message": "Feedback successully deleted"}



@app.get("/station", status_code=status.HTTP_200_OK)
async def get_stations():
    """Get all stations

    Returns:
    - All stations coordinates and their corresponding routes
    """
    result = await db.get_stations()
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
             
    return {"message": "Successfully gathered info about bus stops", "content":{
        "type": "FeatureCollection",
        "features": features 
    }}
    

@app.post("/app_feedback")
async def app_feedback(feedback: Annotated[str, Body(embed=True)]):
    await db.add_app_feedback(feedback)


@app.get("/time/driving", status_code=status.HTTP_200_OK)
async def vehicle_time(route_id:int, long1:float, lat1:float, long2:float, lat2:float, response: Response):
    """Get the driving time from point A to point B by 
    following a specific route

    Parameters:
    - route_id: the id of the chosen route
    - [long1, lat1]: coordinates of the departure
    - [long2, lat2]: coordinates of the destination

    Returns:
    - Eta of the driver
    """
    # Load route
    if route_id not in app.state.routes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error_code": "INVALID_ROUTE_ID",
                                    "msg": "The given route id is invalid"})
    point1 = helper.project_point_on_route((long1, lat1), route_id)
    point2 = helper.project_point_on_route((long2, lat2), route_id)
    eta = helper.get_time_estimation(route_id, point1, point2, MAPBOX_TOKEN)
    return {"message": "All Good.", "time_estimation" : eta}



@app.get("/time/walking", status_code=status.HTTP_200_OK)
async def vehicle_time(long1:float, lat1:float, long2:float, lat2:float):
    """Get the walking time from point A to point B

    Parameters:
    - [long1, lat1]: coordinates of the departure
    - [long2, lat2]: coordinates of the destination

    Returns:
    - Eta of the walk
    """
    return {"message": "All Good.", "time_estimation" : helper.eta([(long1, lat1), (long2, lat2)], os.getenv("mapbox_token"), "walking")}

