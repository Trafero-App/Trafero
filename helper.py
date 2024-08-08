import math
import requests
from db_layer import db
from dotenv import load_dotenv, find_dotenv
import os
from copy import deepcopy
from fastapi import Response, status
import asyncpg

load_dotenv(find_dotenv())

def haversine(pointA, pointB):
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


def project_point_on_route(point, route):
    minimum_distance = float('inf')
    for i,route_point in enumerate(route):
        temp_distance = haversine(point, route_point)
        if temp_distance <= minimum_distance :
            minimum_distance = temp_distance
            closest_point_index = i
    return (closest_point_index, minimum_distance)




def trim_waypoints_list(waypoints, start, end, route=None, start_projection_index=None, end_projection_index=None):
    if start_projection_index is None:
        start_projection_index = project_point_on_route(start, route)[0]
    if end_projection_index is None:
        end_projection_index = project_point_on_route(end, route)[0]

    if start_projection_index == end_projection_index:
        return None
    
    if start == waypoints[0][:2]:
            start_way_point_index = 0
    else:
        for i, way_point in enumerate(waypoints):
            if way_point[2] > start_projection_index:
                start_way_point_index = i
                break
        else:
            start_way_point_index = 0

    if end == waypoints[-1][:2]:
            end_way_point_index = len(waypoints)-1
    else:
        for i, way_point in enumerate(waypoints):
            if way_point[2] >= end_projection_index:
                end_way_point_index = i
                break
        else:
            end_way_point_index = -1
    
    return  [tuple(route[start_projection_index]) + (start_projection_index,)] \
            + waypoints[start_way_point_index:end_way_point_index] + \
            [tuple(route[end_projection_index]) + (end_projection_index,)]

#For later use
def get_remaining_route(route, start):
    start_proj_i = project_point_on_route(start, route)[0]
    return route[start_proj_i:]

def geojsonify_vehicle_list(vehicle_list):
    for i, vehicle in enumerate(vehicle_list):
        vehicle_list[i] = {
                            "type": "Feature", 
                            "properties": {
                                 "id": vehicle["id"],
                                 "status": vehicle["status"],
                                 "license_plate" : vehicle["license_plate"]
                                },
                            "geometry": {
                                 "type": "Point",
                                 "coordinates": [
                                      vehicle["longitude"],
                                      vehicle["latitude"]
                                 ] 
                            } }
        if "projection_index" in vehicle:
            vehicle_list[i]["properties"]["TEST"] = vehicle["projection_index"]
        if "passed" in vehicle:
            vehicle_list[i]["properties"]["passed"] = vehicle["passed"]
         
def get_time_estimation(waypoints, token, mode):
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
    return response.json()["routes"][0]["duration"]

def before_on_route(point_a, point_b, route):
    return project_point_on_route(point_a, route)[0] < project_point_on_route(point_b, route)[0]

def filter_vehicles__pick_up(pick_up, vehicles, route):
    vehicles = deepcopy(vehicles)
    long, lat = pick_up

    # Project all vehicles on the route
    for vehicle in vehicles:
        projection_index = project_point_on_route((vehicle["longitude"], vehicle["latitude"]), route)[0]
        vehicle["projection_index"] = projection_index
    print(vehicles)
    projected_pick_up_point_index = project_point_on_route((long, lat), route)[0]

    vehicles.sort(key=lambda x: x["projection_index"], reverse = True)
    for i, vehicle in enumerate(vehicles):
        if vehicle["projection_index"] <= projected_pick_up_point_index:
            break
    vehicles.reverse()
    return vehicles, len(vehicles) - i

async def filter_vehicles__time(cur_location, pick_up, vehicles, route_geojson):
    # print("\n\n\n")
    # print(route_geojson, end="\n\n\n")
    # Assumes vehicles sorted from closest to furthest to pickup point
    route_id = route_geojson["properties"]["route_id"]
    route = route_geojson["geometry"]["coordinates"]
    token = os.getenv("mapbox_token")
    cur_to_pickup_time = get_time_estimation([cur_location, pick_up], token)
    route_waypoints = await db.get_route_waypoints(route_id)

    for i, vehicle in enumerate(vehicles):
        vehicle_to_pickup_waypoints = trim_waypoints_list(route_waypoints, 
                                                          (vehicle["longitude"], vehicle["latitude"]), 
                                                          pick_up, route
                                                          )
        vehicle_to_pickup_time = get_time_estimation(vehicle_to_pickup_waypoints, token)
        print(vehicle_to_pickup_time, vehicle["vehicle_id"], cur_to_pickup_time)
        if vehicle_to_pickup_time > cur_to_pickup_time:
            return vehicles[i:]
    return []

async def feedback(passenger_id: int, vehicle_id: int, response: Response):
    result = await db.get_feedback(passenger_id,vehicle_id)
    if (result is None) or not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "feedback not found."}
    else:
        return {"message": "All Good", "feedback":result}

async def passenger_feedbacks(passenger_id: int, response: Response):
    result = await db.get_passenger_feedbacks(passenger_id)
    if (result is None) or not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "passenger never submitted feedbacks."}
    else:
        return {"message": "All Good", "feedbacks":result}
    
async def vehicle_feedbacks(vehicle_id: int, response: Response):
    result = await db.get_vehicle_feedbacks(vehicle_id)
    if (result is None) or not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "no feedbacks on given vehicle."}
    else:
        return {"message": "All Good", "feedbacks":result}

async def all_feedbacks(response: Response):
    result = await db.get_all_feedbacks()
    if (result is None) or not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "no feedbacks."}
    else:
        return {"message": "All Good", "feedbacks":result}

async def get_nearby_routes_to_1_point(long, lat, radius, routes):
    close_routes = []
    routes_distances = {}
    for route_id, route_data in routes:
        route_coords = route_data["line"]["geometry"]["coordinates"]
        min_distance = project_point_on_route((long, lat), route_coords)[1]
        print("checking " + route_data["route_name"] + "...")
        if min_distance <= radius:
            routes_distances[route_data["route_id"]] = min_distance
            route_vehicles = await db.get_route_vehicles(route_id)
            for vehicle in route_vehicles:
                del vehicle["longitude"]
                del vehicle["latitude"]
            route_data["vehicles"] = route_vehicles
            close_routes.append(route_data)
    close_routes.sort(key=lambda x: routes_distances[x["route_id"]])
    return close_routes


async def get_nearby_routes_to_2_point(long, lat, radius, long2, lat2, radius2, routes):
    close_routes = []
    routes_distances = {}
    for route_id, route_data in routes:
        route_coords = route_data["line"]["geometry"]["coordinates"]
        min_distance = project_point_on_route((long, lat), route_coords)[1]
        min_distance2 = project_point_on_route((long2, lat2), route_coords)[1]
        print("checking " + route_data["route_name"] + "...")
        if min_distance <= radius and min_distance2 <=radius2:
            routes_distances[route_data["route_id"]] = min_distance
            route_vehicles = await db.get_route_vehicles(route_id)
            for vehicle in route_vehicles:
                del vehicle["longitude"]
                del vehicle["latitude"]
            route_data["vehicles"] = route_vehicles
            close_routes.append(route_data)
    close_routes.sort(key=lambda x: routes_distances[x["route_id"]])
    return close_routes
            
