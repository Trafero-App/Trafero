"""
vehicles.py

This module handles all functions related to vehicles information, location and details.

"""

from database import db
from .way_eta import get_time_estimation
from .operations import project_point_on_route






def off_track(vehicle_location, route_id, threshold):
    """
    Check if a vehicle is off track.

    Parameters:
    -vehicle location (long, lat) 
    -route_id
    -threshold

    Returns:
    -Boolean indicating if the vehicle is off track
    """
    if project_point_on_route(vehicle_location, route_id)[1] >= threshold:
        return True
    return False

async def get_vehicle_time_estimation(vehicle_id, dest, token, location = None, route_id = None):
    """
    Get estimated time of arrival (ETA) of a vehicle from it's current location to destination.

    Parameters:
    -vehicle_id  
    -destination (long, lat)
    -MapBox token
    -vehicle_location (optional)
    -route id (optional)

    Returns:
    -Boolean indicating if the vehicle already passed the location, if not, estimated time of arrival (ETA)
    """
    if location == None:
        vehicle_location = await db.get_vehicle_location(vehicle_id)
        location = vehicle_location["longitude"], vehicle_location["latitude"]

    if route_id is None: 
        route_id = await db.get_vehicle_route_id(vehicle_id)

    vehicle_index = project_point_on_route(location, route_id)[0]
    pick_up = project_point_on_route(dest,route_id)[0]
    if vehicle_index > pick_up:
        return {"passed": True}
    
    time_estimation = await get_time_estimation(route_id, vehicle_index, pick_up, token)
    return {"passed": False, "expected_time": time_estimation}

#GOOD
async def get_route_vehicles_eta(pick_up, vehicles, route_id, token):
    """
    Get estimated time of arrival (ETA) of all vehicles on a route to a destination.

    Parameters:
    -pick up location (long, lat)  
    -list of vehicles available
    -route id
    -MapBox token

    Returns:
    -For each vehicle, boolean indicating if the vehicle already passed the location, if not, estimated time of arrival (ETA)
    """
    available = []
    passed = []
    for vehicle in vehicles:
        id = vehicle["id"]
        location = (vehicle["longitude"], vehicle["latitude"])
        del vehicle["longitude"]
        del vehicle["latitude"]
        v_eta = await get_vehicle_time_estimation(id, pick_up, token, location, route_id)
        if v_eta["passed"] == True:
            vehicle["passed"] = True
            passed.append(vehicle)
        else:
            vehicle["passed"] = False
            vehicle["expected_time"] = v_eta["expected_time"]
            available.append(vehicle)
    
    available.sort(key=lambda x: x["expected_time"])
    return available + passed
           

async def all_vehicles_info():
    """
    Get information for all vehicles.
    
    """
    vehicle_info = await db.get_all_vehicles_info()
    features = []
    for vehicle in vehicle_info:
        route_id = await db.get_vehicle_route_id(vehicle["id"])
        route_coords = db.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]
        if vehicle["status"] != "inactive":
            vehicle_coords = route_coords[project_point_on_route((vehicle["longitude"], vehicle["latitude"]), route_id)[0]]
        else:
            vehicle_coords = (vehicle["longitude"], vehicle["latitude"])

        features.append({
            "type": "Feature",
            "properties": {
                "status": vehicle["status"],
                "id": vehicle["id"]
            },
            "geometry": {
                "coordinates": vehicle_coords,
                "type": "Point"
            
            }
        })

    return {
                "type": "FeatureCollection",
                "features": features
                    
            }