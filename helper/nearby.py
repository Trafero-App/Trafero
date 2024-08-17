"""
nearby_routes.py

This module handles all functions and operations related to nearby routes.

"""

from database import db
from copy import deepcopy
from collections import namedtuple
from typing import List
from .operations import project_point_on_route
from .way_eta import get_time_estimation
from .routes import get_route_details

Chain = namedtuple("Chain", ["route1_id", "route1_intersection", "route2_id", "route2_intersection", "pickup_index", "dest_index"])


def nearby_routes_to_a_point(long, lat, radius, turn_to_dict=False):
    """
    Find all routes within a specified radius from a given location.

    Parameters:
    - [long, lat]: coordinates of given location.
    - radius: The radius controlling serach area.
    - turn_to_dict (optional): If True, converts the list of nearby routes to a dictionary.

    Returns:
    All nearby routes, sorted by their distance from the location. 

    """
    nearby_routes = []
    routes_distances = {}
    for route_id in db.routes:
        point_index, min_distance = project_point_on_route((long, lat), route_id)
        
        if min_distance <= radius:
            nearby_routes.append((route_id, point_index))
            routes_distances[route_id] = min_distance
    
    nearby_routes.sort(key=lambda route: routes_distances[route[0]])

    if turn_to_dict:
        nearby_routes = {route[0]: route[1] for route in nearby_routes}

    return nearby_routes


async def nearby_routes_to_a_point_formated(long, lat, radius):
    """
    Find all routes within a specified radius from a given location.

    Parameters:
    - [long, lat]: coordinates of given location.
    - radius: The radius controlling search area.

    Returns:
    All nearby routes, sorted by their distance from the location. 

    """
    routes = nearby_routes_to_a_point(long, lat, radius)
    formated_nearby_routes = []
    for route_id, _ in routes:
        route_output_data = await get_route_details(route_id)
        formated_nearby_routes.append(route_output_data)
    return formated_nearby_routes

async def direct_nearby_routes_to_2_point(long, lat, radius, long2, lat2, radius2, mapbox_token):
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
    routes_near_A = nearby_routes_to_a_point(long, lat, radius, True)
    routes_near_B = nearby_routes_to_a_point(long2, lat2, radius2, True)

    for route_id in routes_near_A:
        if route_id not in routes_near_B: continue

        start_index = routes_near_A[route_id] 
        end_index = routes_near_B[route_id]

        if end_index < start_index: continue        
        
        route_details = await get_route_details(route_id)
        eta = await get_time_estimation(route_id, start_index, end_index, mapbox_token)
        route_details["chain"] = False
        route_details["eta"] = eta           
        routes.append(route_details)

    return routes




def find_all_chains(intersection_data, routes_A, routes_B):
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
            if id_B in routes_A: continue
            pickup_index, destination_index = routes_A[id_A], routes_B[id_B]
            for route1_id, route1_intersection, route2_id, route2_intersection in intersection_data:
                    if route1_id != id_A or route2_id != id_B: continue
                    if pickup_index > route1_intersection or destination_index < route2_intersection: continue
                    chain = Chain(route1_id, route1_intersection, route2_id, route2_intersection, pickup_index, destination_index)
                    valid_chains.append(chain)

    return valid_chains

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
                length_1 = chain2.route1_intersection - chain1.pickup_index + chain1.dest_index - chain1.route2_intersection
                length_2 = chain2.route1_intersection - chain2.pickup_index + chain2.dest_index - chain2.route2_intersection
                if length_1 < length_2:
                    filtered_chains.remove(chain2)
                else:
                    filtered_chains.remove(chain1)
    return filtered_chains

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
    chains = find_all_chains(intersections, nearby_A, nearby_B)
    filtered_chains: List[Chain] = await filter_duplicate_chains(chains)
    chained_output = []
    for chain in filtered_chains:

        route1_id = chain.route1_id
        route1_data = await get_route_details(route1_id, 1)
        eta1 = await get_time_estimation(route1_id, chain.pickup_index, chain.route1_intersection, mapbox_token)
        sliced_1 = route1_data["line1"]["features"][0]["geometry"]["coordinates"][chain.pickup_index : chain.route1_intersection + 1]
        route1_data["eta1"] = eta1

        route2_id = chain.route2_id
        route2_data = await get_route_details(route2_id, 2)
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
                  "properties": {"order": 1},
                  "geometry": {
                    "coordinates": sliced_1,
                    "type": "LineString"
                  }
                },
                {
                  "type": "Feature",
                  "properties": {"order": 2},
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

async def all_nearby_routes_2_points(long, lat, radius, long2, lat2, radius2, mapbox_token):
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
    routes_near_A = nearby_routes_to_a_point(long, lat, radius, mapbox_token)
    routes_near_B = nearby_routes_to_a_point(long2, lat2, radius2, mapbox_token)

    close_direct_routes = await direct_nearby_routes_to_2_point(long, lat, radius, long2, lat2, radius2, mapbox_token)
    close_chained_routes = await chained_routes(intersections, routes_near_A, routes_near_B, mapbox_token)

    all_routes = close_direct_routes + close_chained_routes
    all_routes.sort(key=lambda route: route["eta"])
    return all_routes
