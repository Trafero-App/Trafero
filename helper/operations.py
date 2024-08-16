"""
main.py

This module handles fundamental functions related to basic coordinaates operations.

"""
import math
from database import db

#GOOD
def haversine(pointA, pointB):
    """
    Calculate distance between two geographical points.

    Parameters:
    -pointA (long, lat) 
    -pointB (long, lat)

    Returns:
    -Distance between points in meters
    """
    lon1 = pointA[0]
    lat1 = pointA[1]
    lon2 = pointB[0]
    lat2 = pointB[1]
    R = 6371.0 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c * 1000
    return distance

#GOOD
def project_point_on_route(point, route_id):
    """
    Calculate the projection of a point on a certain route.

    Parameters:
    -point (long, lat) 
    -route_id

    Returns:
    -Coordinates of the projected point
    """
    route_coords = db.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]
    minimum_distance = float('inf')
    for i,route_point in enumerate(route_coords):
        temp_distance = haversine(point, route_point)
        if temp_distance <= minimum_distance :
            minimum_distance = temp_distance
            closest_point_index = i
    return (closest_point_index, minimum_distance)
