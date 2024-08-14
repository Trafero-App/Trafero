from fastapi import FastAPI, Response, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
import asyncpg
import os
from dotenv import load_dotenv, find_dotenv

from typing import Annotated, Literal, List
from validation import is_valid_password, is_valid_dob, is_valid_email, is_valid_name, \
is_valid_phone_number, Account_Info, Point, Account_DB_Entry, Passenger_Review, Review_DB_Entry

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
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If username is already in use. (status code: 409)
    - HTTPException: If phone number is already in use. (status code: 409)
    - HTTPException: If email is already in use. (status code: 409)
    """
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
        is_available_email = await db.check_email_available(account_data.email, account_data.account_type)
        if not is_available_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"error_code": "EMAIL_UNAVAILABLE",
                                        "msg":"The email you attempted to sign-up with is already used by another user."
                                        }
                                )
 
    password_hash = authentication.hash_password(account_data.password)
    user_id = await db.add_account(Account_DB_Entry(**account_data.model_dump(exclude={"password"}), password_hash=password_hash))
    token_data = {"sub": user_id, "type": account_data.account_type}
    access_token = authentication.create_access_token(token_data)
    if account_data.account_type == "vehicle":
        await db.add_vehicle_location(user_id, None, None)
    return {"message": "Account was signed up successfully.", "token": {"access_token": access_token, "token_type": "bearer"}}
    
@app.get("/check_email/{account_type}", status_code=status.HTTP_200_OK)
async def check_email(account_type: Literal["passenger", "vehicle"], email: str):
    """Check if email has proper form and is unused"""
    has_proper_form = is_valid_phone_number(email)
    is_unused = await db.check_email_available(email, account_type)
    return {"message": "Validating email complete.", "is_valid": has_proper_form and is_unused}

@app.get("/check_phone_number/{account_type}", status_code=status.HTTP_200_OK)
async def check_phone_number(account_type: Literal["passenger", "vehicle"], phone_number: str):
    """Check if phone number has proper form and is unused"""
    has_proper_form = is_valid_phone_number(phone_number)
    is_unused = await db.check_phone_number_available(phone_number, account_type)
    return {"message": "Validating email complete.", "is_valid": has_proper_form and is_unused}

@app.get("/check_password", status_code=status.HTTP_200_OK)
async def check_password(password: str):
    """Check if password has proper form
    """
    return {"message": "Validating email complete.", "is_valid": helper.is_valid_password(password)}


@app.post("/login/{account_type}", status_code=status.HTTP_200_OK)
async def login(account_type: Literal["passenger", "vehicle"], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Validate user credentials and provide authentication token

    Parameters:
    - account_type: specifies if the user is attempting to log in
      as a passenger or as a vehicle
    - form_data: data containing user credentials (username and password)

    Returns:
    - Authentication token

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If credentials are invalid (status code: 401)
    """
    # Find login method
    identifier = form_data.username
    if helper.is_valid_phone_number(identifier): login_method = "phone_number"
    else: login_method = "email"

    user = await authentication.check_user_credentials(form_data.username, form_data.password, account_type, login_method)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error_code": "INVALID_CREDENTIALS",
                                                                              "msg": "The entered credentials are invalid"})
    token_data = {"sub": user["id"], "type": account_type}
    access_token = authentication.create_access_token(token_data)
    return {"message": "Token generated successfully.", "token": {"access_token": access_token, "token_type": "bearer"}}

@app.get("/account_info")
async def get_account_info(user_info: authentication.authorize_any_account):
    """Gives account info"""
    del user_info["password_hash"]
    if user_info["account_type"] == "vehicle": # user is a vehicle
        user_info["route_list"] = [{"route_id": route_id,
                                    "name": db.routes[route_id]["details"]["route_name"],
                                    "description": db.routes[route_id]["details"]["description"],
                                    "line": db.routes[route_id]["line"]
                                    } for route_id in user_info["route_list"]]
    return user_info


@app.get("/vehicle_location/{vehicle_id}", status_code=status.HTTP_200_OK)
async def get_vehicle_location(vehicle_id: int):
    """Get the location of the vehicle having id `vehicle_id`

    Parameters:
    - vehicle_id: id of the vehicle whose location is needed

    Returns:
    - [long, lat] representing the vehicle's coordinates

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If the entered vehicle id doesn't correspond to a valid vehicle
      in the database (status code: 404)

    """
    entry = await db.get_vehicle_location(vehicle_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error_code": "INVALID_VEHICLE_ID", "msg": f"'{vehicle_id}' isn't a valid vehicle id"})
    
    return {"message": "Coordinates found successfully.", "coordinates":[entry["longitude"], entry["latitude"]]}

@app.post("/vehicle_location", status_code=status.HTTP_200_OK)
async def post_vehicle_location(vehicle_location_data: Point, user_info : authentication.authorize_vehicle):
    """Add the location of an existing vehicle to the database

    Parameters:
    - vehicle_location_data: A `Point` representing the vehicle's location
    - user_info: user information extracted from the authentication token

    Returns:
    - Message indicating the location was succesfully added
    
    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If the request doesn't include a valid vehicle account
      unexpired access token (status code: 401)
    - HTTPException: If the location of the vehicle has already been added (status code: 400)
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
                                    "msg": "The vehicle id used is invalid. Try to generate another token."})
    return {"message": "All Good."}


@app.put("/vehicle_location", status_code=status.HTTP_200_OK)
async def put_vehicle_location(vehicle_location_data: Point, user_info : authentication.authorize_vehicle):
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
    vehicle_id = user_info["id"]
    latitude, longitude = vehicle_location_data.latitude, vehicle_location_data.longitude
    success = await db.update_vehicle_location(vehicle_id, longitude=longitude, latitude=latitude)
    # False signifies that you tried to update the location of a vehicle whose location isn't in the db yet
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail={"error_code": "LOCATION_NOT_ADDED_PREVIOUSLY",
                                    "msg": "Your location has not been added previously. Maybe you meant to send a POST request?"})
    else:   
        route_id = await db.get_vehicle_route_id(vehicle_id)
        route = app.state.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]
        if helper.off_track((longitude, latitude), route, VEHICLE_TO_ROUTE_THRESHOLD):
            await db.update_status(vehicle_id, "unknown")
            return {"message": "Location succesfully updated. Status set to unknown: you are too far from your route."}
        else:
            return {"message": "Location succesfully updated."}


@app.put("/vehicle_status", status_code=status.HTTP_200_OK)
async def put_vehicle_status(vehicle_id: int, new_status: Literal["active", "waiting", "unavailable", "inactive", "unknown"]): # to be changed
    """Update vehicle status

    Parameters:
    - vehicle_id: id of the vehicle whose status is to be updated
    - new_status: the status the vehicle should take on

    Returns:
    - Message indicating the status was successfully updated

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: If no vehicle with the given id is found (status code: 404)
    """
    success = await db.update_status(vehicle_id, new_status)
    if success:
        return {"message": "Status updated successfully."}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error_code": "INVALID_VEHICLE_ID",
                                    "msg":"Please provide a valid vehicle id"}) # to be changed


@app.put("/active_route", status_code=status.HTTP_200_OK)
async def change_active_route (new_active_route: int, user_info : authentication.authorize_vehicle):
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
    vehicle_id = user_info["id"]
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
async def add_vehicle_route(new_routes: List[int], user_info: authentication.authorize_vehicle):
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
    vehicle_id = user_info["id"]
    try:
        await db.set_route(vehicle_id, new_routes)
    except asyncpg.exceptions.ForeignKeyViolationError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error_code": "INVALID_ROUTE_ID",
                                    "msg": "One of the route ids given is invalid"})
    return {"message": f"Successfully replaced your route_list with {new_routes}"}


@app.get("/route_details/{route_id}", status_code=status.HTTP_200_OK)
async def route_details(route_id: int):
    """Get details of a specific route

    Parameters:
    - route_id: the id of the route whose details are requested

    Returns:
    - The data of the requested route

    Raises:
    - HTTPException: If the route id is invalid (status code: 404)
    """
    if route_id not in app.state.routes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error_code": "INVALID_ROUTE_ID",
                                    "msg": "The given route id is invalid"})
    
    route_data = helper.flatten_route_data(app.state.routes[route_id])

    return {"message" : f"Successfully collected the route data of the route with id {route_id}",
            "route_data": route_data}



@app.get("/route/{route_id}", status_code=status.HTTP_200_OK)
async def route(route_id: int):
    """Get some information about a route and about the 
       vehicles currently on it

    Parameters:
    - route_id: The id of the route whose information is requested

    Returns:
    - The requested info described above

    Raises:
    - HTTPException: If the input is not in the correct structure (status code: 422)
    - HTTPException: if the given route_id is invalid (status_code: 404)
    """
    if route_id not in app.state.routes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error_code": "INVALID_ROUTE_ID",
                                    "details": "The given route id is invalid"})
    
    route_data = app.state.routes[route_id]
    route_needed_data = {"description": route_data["details"]["description"],
                         "line": route_data["line"],
                         "route_id": route_id,
                         "route_name": route_data["details"]["route_name"],
                         }
    route_vehicles = await db.get_route_vehicles(route_id)
    for vehicle in route_vehicles:
        del vehicle["latitude"]
        del vehicle["longitude"]
    route_needed_data["vehicles"] = route_vehicles
    return {"message" : f"Successfully collected the data of the route with id {route_id} and its vehicles",
            "route_data": route_needed_data}



@app.get("/all_vehicles_location", status_code=status.HTTP_200_OK)
async def all_vehicles_location():
    """Get the location and status of all vehicles"""
    vehicle_info = await db.get_all_vehicles_info()
    features = []
    for vehicle in vehicle_info:
        route_id = await db.get_vehicle_route_id(vehicle["id"])
        route_coords = app.state.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]
        features.append({
            "type": "Feature",
            "properties": {
                "status": vehicle["status"],
                "id": vehicle["id"]
            },
            "geometry": {
                "coordinates": route_coords[helper.project_point_on_route((vehicle["longitude"], vehicle["latitude"]), route_coords)[0]]
                ,
                "type": "Point"
            
            }
        })

    return {"message": "All good.",
            "content": {
                "type": "FeatureCollection",
                "features": features
                    
            }
        }


@app.get("/route_vehicles_eta/{route_id}", status_code=status.HTTP_200_OK)
async def route_vehicles_eta(route_id:int, response: Response,
                             pick_up_long:float, pick_up_lat:float):
    """Get the etas of all busses on a specific route to
    a specific destination

    Parameters:
    - route_id: the id of the route whose vehicle etas are requested
    - [pick_up_long, pick_up_lat]: coordinates of the destination

    Returns:
    - The eta of every vehicle to the destination. If the vehicle,
      already
    """
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

    route = app.state.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]
    vehicles, av_vehicles_last_i = helper.filter_vehicles__pick_up((pick_up_long, pick_up_lat), vehicles, route)
    waypoints = await db.get_route_waypoints(route_id)
    for i in range(av_vehicles_last_i):
        vehicle = vehicles[i]

        vehicle["expected_time"] =  await helper.get_vehicle_time_estimation(vehicle["id"], (pick_up_long, pick_up_lat), MAPBOX_TOKEN, waypoints)
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
async def get_vehicle(vehicle_id: int, response: Response, user_info: authentication.authorize_anyone):
    if user_info is not None and user_info["type"] == "passenger":
        passenger_id = user_info.get("id")
    else: passenger_id = None
    vehicle_details = await db.get_vehicle_details(vehicle_id)
    if vehicle_details is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail={"error_code": "INVALID_VEHICLE_ID",
                              "details": "The given vehicle id is invalid"})
    vehicle_route = app.state.routes[vehicle_details["route_id"]]
    vehicle_details["route_name"] = vehicle_route["details"]["route_name"]
    if passenger_id is not None:
        vehicle_details["user_choice"] = (await db.get_passenger_reaction(passenger_id, vehicle_id))["reaction"]
    else:
        vehicle_details["user_choice"] = None

    vehicle_details["remaining_route"] = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "LineString",
            "coordinates": helper.get_remaining_route(vehicle_route["line"]["features"][0]["geometry"]["coordinates"], vehicle_details["coordinates"])
        }
    }
    return {"message": "All Good", "content": vehicle_details}


@app.get("/time/driving", status_code=status.HTTP_200_OK)
async def vehicle_time(route_id:int, long1:float, lat1:float, long2:float, lat2:float, response: Response):
    # Load route
    if route_id not in app.state.routes:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Route not found."}
    route = app.state.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]
    waypoints = await db.get_route_waypoints(route_id)
    waypoints = helper.trim_waypoints_list(waypoints, (long1, lat1), (long2, lat2), route)
    return {"message": "All Good.", "time_estimation" : helper.get_time_estimation(waypoints, MAPBOX_TOKEN, "driving")}


@app.get("/time/walking", status_code=status.HTTP_200_OK)
async def vehicle_time(long1:float, lat1:float, long2:float, lat2:float, response: Response):
    return {"message": "All Good.", "time_estimation" : helper.get_time_estimation([(long1, lat1), (long2, lat2)], os.getenv("mapbox_token"), "walking")}

@app.get("/vehicle_eta/{vehicle_id}")
async def vehicle_eta(vehicle_id: int, pick_up_long:float, pick_up_lat:float):
    passed = await helper.check_vehicle_passed(vehicle_id, (pick_up_long, pick_up_lat))
    if passed:
        return {
            "message": "All good.",
            "content": {"passed": True}
        }
    else:
        time_estimation = await helper.get_vehicle_time_estimation(vehicle_id, (pick_up_long, pick_up_lat), MAPBOX_TOKEN)
        return {
            "message": "All good.",
            "content":{
                "passed": False,
                "expected_time": time_estimation
                }
        }


@app.get("/nearby_routes", status_code=status.HTTP_200_OK)
async def nearby_routes(long:float, lat:float, radius:float, 
                        long2: float | None=None, lat2: float|None = None, radius2: float|None=None):
    if long2 is not None and lat2 is not None and radius2 is not None:
        close_routes = await helper.get_nearby_routes(long, lat, radius, long2, lat2, radius2, app.state.routes, MAPBOX_TOKEN)
    else:
        close_routes = await helper.get_nearby_routes_to_1_point(long, lat, radius, app.state.routes)
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
    success = await db.delete_feedback(passenger_id, vehicle_id)
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