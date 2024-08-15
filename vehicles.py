import math
from db_layer import db
from way_eta import get_eta
from operations import project_point_on_route





# VEHICLES
#GOOD
def off_track(vehicle_location, route_id, threshold):
    route = db.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]
    if project_point_on_route(vehicle_location, route)[1] >= threshold:
        return True
    return False

#GOOD
async def get_vehicle_time_estimation(vehicle_id, dest, token, location = None, route_id = None):
    if location == None:
        vehicle_location = await db.get_vehicle_location(vehicle_id)
        location = vehicle_location["longitude"], vehicle_location["latitude"]

    if route_id is None: 
        route_id = await db.get_vehicle_route_id(vehicle_id)

    vehicle_index = project_point_on_route(location, route_id)[0]
    pick_up = project_point_on_route(dest,route_id)[0]
    if vehicle_index > pick_up:
        return {"passed": True}
    
    time_estimation = await get_eta(route_id, vehicle_index, pick_up, token)
    return {"passed": False, "expected_time": time_estimation}

#GOOD
async def get_route_vehicles_eta(pick_up, vehicles, route_id, token):
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
    vehicle_info = await db.get_all_vehicles_info()
    features = []
    for vehicle in vehicle_info:
        route_id = await db.get_vehicle_route_id(vehicle["id"])
        route_coords = db.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]
        features.append({
            "type": "Feature",
            "properties": {
                "status": vehicle["status"],
                "id": vehicle["id"]
            },
            "geometry": {
                "coordinates": route_coords[project_point_on_route((vehicle["longitude"], vehicle["latitude"]), route_id)[0]]
                ,
                "type": "Point"
            
            }
        })

    return {
                "type": "FeatureCollection",
                "features": features
                    
            }