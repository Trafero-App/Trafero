"""
routes.py

This module handles all functions related to routes operations.

"""
from db_layer import db
from operations import project_point_on_route

#GOOD
def get_remaining_route(route_id, start):
    """Get remaining part of a certain route based on a start location.

    Parameters:
    - route id 
    - start location (long, lat) 

    Returns:
    - Remaining part of a the route.
    """
    routes = db.routes
    start_proj_i = project_point_on_route(start, route_id)[0]
    remaining_route = routes[route_id]["line"]["features"][0]["geometry"]["coordinates"][start_proj_i:]
    out = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "LineString",
            "coordinates": remaining_route
        }
    }
    return out

#GOOD
def flatten_route_data(route):
    res: dict = route["details"].copy()
    res["line"]= route["line"]
    return res

#GOOD
async def get_route_data(route_id, num=''):
    """Get specific details of a certain route.

    Parameters:
    - route id  

    Returns:
    - Selected details of chosen route.
    """
    routes = db.routes
    route_vehicles = await db.get_route_vehicles(route_id)
    for vehicle in route_vehicles:
        del vehicle["longitude"]
        del vehicle["latitude"]
    
    route_name = routes[route_id]["details"]["route_name"]
    description = routes[route_id]["details"]["description"]
    line = routes[route_id]["line"]
    route_data = {
                            f"route_id{num}": route_id,
                            f"route_name{num}": route_name,
                            f"description{num}": description,
                            f"vehicles{num}": route_vehicles,
                            f"line{num}": line
                            }
    return route_data