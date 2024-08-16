"""
waypoints_eta.py

This module handles all functionalities related to waypoint and time estimation

"""

import requests
from database import db
from .operations import project_point_on_route 



async def get_time_estimation(route_id, start_index, end_index, mapbox_token):
    """
    Get estimated time of arrival (ETA) for a specific route segment.

    Parameters:
    -route_id 
    -start_index 
    -end_index 
    -mapbox_token: The Mapbox API token used for calculating ETA.

    """
    waypoints = await db.get_route_waypoints(route_id)
    trimed_waypoints = trim_waypoints(waypoints, route_id, start_index, end_index)
    eta = eta(trimed_waypoints, mapbox_token, "driving")
    return eta


def trim_waypoints(waypoints, route_id, start_index, end_index):
    """
    Extract a subset of waypoints from the route based on the provided start and end indices.
    
    Parameters:
    -waypoints 
    -route_id 
    -start_index 
    -end_index 

    Returns:
    -Trimmed waypoints of the route, if waypoints not available returns None.
    """
    route_coords = db.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]

    if start_index == end_index:
        return None
    if start_index == waypoints[0][2]:
            start_waypoint = 0
    else:
        for i, way_point in enumerate(waypoints):
            if way_point[2] > start_index:
                start_waypoint = i
                break
        else:
            start_waypoint = 0
    if end_index == waypoints[-1][2]:
            end_waypoint = -1
    else:
        for i, way_point in enumerate(waypoints):
            if way_point[2] >= end_index:
                end_waypoint = i
                break
        else:
            end_waypoint = -1
    new_waypoints = [tuple(route_coords[start_index]) + (start_index,)] \
            + waypoints[start_waypoint:end_waypoint] + \
            [tuple(route_coords[end_index]) + (end_index,)]
    
    return new_waypoints



def eta(waypoints, token, mode):
    """
    Direct request to get estimated time of arrival (ETA) from MapBox api.
    
    Parameters:
    -waypoints 
    -MapBox token
    -mode of transportation

    Returns:
    -Estimated time of arrival (ETA).
    """
    if waypoints == None:
        return 0
    if mode == "driving": mapbox_mode = "driving-traffic"
    elif mode == "walking": mapbox_mode = "walking"
    url = f"https://api.mapbox.com/directions/v5/mapbox/{mapbox_mode}/" + \
    ';'.join([",".join(map(str, x[:2])) for x in waypoints])
    url += "?alternatives=false" # Don't search for alternative routes
    url += "&continue_straight=true" # Tend to continue in the same direction
    url += "&steps=false" # Don't include turn-by-turn instrutions
    params = {'access_token': token,
              'geometries': 'geojson',
              'overview': 'full'
              }
    response = requests.get(url, params=params)
    # print(response.json())
    return round(response.json()["routes"][0]["duration"] / 60)