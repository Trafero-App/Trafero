"""
nearby_routes.py

This module handles all functions and operations related to nearby routes.

"""
from db_layer import db
from copy import deepcopy
from collections import namedtuple
from typing import List
from way_eta import get_time_estimation
from operations import project_point_on_route
from routes import get_route_data

Chain = namedtuple("Chain", ["route1_id", "route1_intersection", "route2_id", "route2_intersection", "pickup_index", "dest_index"])






def nearby_routes(long, lat, radius, turn_to_dict=False):
    """
    Find all routes within a specified radius from a given location.

    Parameters:
    - [long, lat]: coordinates of given location.
    - radius: The radius controlling serach area.
    - turn_to_dict (optional): If True, converts the list of nearby routes to a dictionary.

    Returns:
    All nearby routes, sorted by their distance from the location. 

    """
    routes = db.routes
    nearby_routes = []
    routes_distances = {}
    for route_id in routes:
        proj_index, min_distance = project_point_on_route((long, lat), route_id)
        
        if min_distance <= radius:
            nearby_routes.append((route_id, proj_index))
            routes_distances[route_id] = min_distance
    nearby_routes.sort(key=lambda route: routes_distances[route[0]])
    if turn_to_dict:
        L = deepcopy(nearby_routes)
        nearby_routes = {route[0]: route[1] for route in L}
    return (nearby_routes)

#GOOD
async def get_nearby_routes_to_1_point(long, lat, radius):
    """
    Find all routes within a specified radius from a given location.

    Parameters:
    - [long, lat]: coordinates of given location.
    - radius: The radius controlling search area.

    Returns:
    All nearby routes, sorted by their distance from the location. 

    """
    routes = nearby_routes(long, lat, radius)
    formated_nearby_routes = []
    for route_id, _ in routes:
        route_output_data = await get_route_data(route_id)
        formated_nearby_routes.append(route_output_data)
    return formated_nearby_routes

#GOOD
async def get_nearby_routes_to_2_point(long, lat, radius, long2, lat2, radius2, mapbox_token):
    """
    Find all routes that pass from A to B within a specified radius from a given location.

    Parameters:
    - [long, lat]: coordinates of first location.
    - radius: The radius controlling search area of first location.
    - [long2, lat2]: coordinates of second location.
    - radius: The radius controlling search area of second location.
    - MapBox token: used to get estimated time of arrival (ETA).

    Returns:
    All nearby routes, sorted by their estimated time of arrival (ETA). 

    """
    routes = []
    routes_A = nearby_routes(long, lat, radius, True)
    routes_B = nearby_routes(long2, lat2, radius2, True)

    for route_id in routes_A:
        if route_id not in routes_B: continue
        start_index = routes_A[route_id] 
        end_index = routes_B[route_id]
        if end_index < start_index: continue        
        route_data = await get_route_data(route_id)
        eta = await get_time_estimation(route_id, start_index, end_index, mapbox_token)
        route_data["chain"] = False
        route_data["eta"] = eta           
        routes.append(route_data)

    return routes




#GOOD
def chainer(intersection_data, routes_A, routes_B):
    """
    Find all combinations of chained routes.

    Parameters:
    - intersections data: All info about intersections between routes.
    - nearby_A: all routes nearby A.
    - nearby_B: all routes nearby B.

    Returns:
    All combinations of chained routes. 

    """
    valid_chains = []
    for id_A in routes_A:
        if id_A in routes_B: continue
        for id_B in routes_B:
            pickup_index, destination_index = routes_A[id_A], routes_B[id_B]
            for route1_id, route1_intersection, route2_id, route2_intersection in intersection_data:
                    if route1_id != id_A or route2_id != id_B: continue
                    if pickup_index > route1_intersection or destination_index < route2_intersection: continue
                    chain = Chain(*map(int, (route1_id, route1_intersection, route2_id, route2_intersection, pickup_index, destination_index)))
                    valid_chains.append(chain)

    return valid_chains

#GOOD
async def filter_duplicate_chains(chains):
    """
    Filter combinations of chained routes.

    Parameters:
    - chains: All chaining combinations.

    Returns:
    Fileterd combinations of chained routes. 

    """
    filtered_chains = chains.copy()
    for i, chain1 in enumerate(chains):
        for chain2 in chains[i + 1:]:
            if chain1.route1_id == chain2.route1_id and chain1.route2_id == chain2.route2_id:
                lenght_1 = chain2.route1_intersection - chain1.pickup_index + chain1.dest_index - chain1.route2_intersection
                lenght_2 = chain2.route1_intersection - chain2.pickup_index + chain2.dest_index - chain2.route2_intersection
                if lenght_1 < lenght_2:
                    filtered_chains.remove(chain2)
                else:
                    filtered_chains.remove(chain1)
    return filtered_chains

#GOOD
async def chained_routes(intersections, nearby_A, nearby_B, mapbox_token):
    """
    get filtered combinations of routes chaining to go from A to B.

    Parameters:
    - intersections: All info about intersections between routes.
    - nearby_A: all routes nearby A.
    - nearby_B: all routes nearby B.
    - MapBox token: used to get estimated time of arrival (ETA).

    Returns:
    All chained nearby routes, sorted by their estimated time of arrival (ETA). 

    """
    chains = chainer(intersections, nearby_A, nearby_B)
    filtered_chains: List[Chain] = await filter_duplicate_chains(chains)
    chained_output = []

    for chain in enumerate(filtered_chains):

        route1_id = chain.route1_id
        route1_data = await get_route_data(route1_id, 1)
        eta1 = await get_time_estimation(route1_id, chain.pickup_index, chain.route1_intersection, mapbox_token)
        sliced_1 = route1_data["line1"]["features"][0]["geometry"]["coordinates"][chain.pickup_index : chain.route1_intersection + 1]
        route1_data["eta1"] = eta1

        route2_id = chain.route2_id
        route2_data = await get_route_data(route2_id, 2)
        eta2 = await get_time_estimation(route2_id, chain.route2_intersection, chain.dest_index, mapbox_token)
        sliced_2 = route2_data["line2"]["features"][0]["geometry"]["coordinates"][chain.route2_intersection : chain.dest_index + 1]
        route2_data["eta2"] = eta2

        common = {
            "chain": True,
            "eta": eta1 + eta2,
            "line": {
              "type": "FeatureCollection",
              "features": [
                {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "coordinates": sliced_1,
                    "type": "LineString"
                  }
                },
                {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "coordinates": sliced_2,
                    "type": "LineString"
                  }
                }
              ]
            }
        }

        formated_output = {**route1_data, **route2_data, **common}
        
        chained_output.append(formated_output)    

    return chained_output

#GOOD
async def get_nearby_routes(long, lat, radius, long2, lat2, radius2, mapbox_token):
    """
    Get all possible direct and chained routes going from A to B by calling above functions.

    Parameters:
    - [long, lat]: coordinates of first location.
    - radius: The radius controlling search area of first location.
    - [long2, lat2]: coordinates of second location.
    - radius: The radius controlling search area of second location.
    - MapBox token: used to get estimated time of arrival (ETA).

    Returns:
    All direct and chained nearby routes, sorted by their estimated time of arrival (ETA). 

    """
    intersections = await db.get_intersections()
    nearby_A = nearby_routes(long, lat, radius, mapbox_token)
    nearby_B = nearby_routes(long2, lat2, radius2, mapbox_token)

    close_routes = await get_nearby_routes_to_2_point(long, lat, radius, long2, lat2, radius2, mapbox_token)
    chained_close_routes = await chained_routes(intersections, nearby_A, nearby_B, mapbox_token)

    total = close_routes + chained_close_routes
    total.sort(key=lambda route: route["eta"])
    return total