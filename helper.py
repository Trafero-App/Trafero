import math
import requests
from db_layer import db
from dotenv import load_dotenv, find_dotenv
import os
from copy import deepcopy
from fuzzywuzzy import fuzz, process
from collections import namedtuple
from typing import List
import regex as re
from typing import Literal

Chain = namedtuple("Chain", ["route1_id", "route1_inter_proj", "route2_id", "route2_inter_proj", "pickup_index", "dest_index"])

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




def trim_waypoints_index(waypoints, route, start_projection_index, end_projection_index):

    if start_projection_index == end_projection_index:
        return None
    
    if start_projection_index == waypoints[0][2]:
            start_way_point_index = 0
    else:
        for i, way_point in enumerate(waypoints):
            if way_point[2] > start_projection_index:
                start_way_point_index = i
                break
        else:
            start_way_point_index = 0

    if end_projection_index == waypoints[-1][2]:
            end_way_point_index = len(waypoints)-1
    else:
        for i, way_point in enumerate(waypoints):
            if way_point[2] >= end_projection_index:
                end_way_point_index = i
                break
        else:
            end_way_point_index = -1
    
    new_waypoints = [tuple(route[start_projection_index]) + (start_projection_index,)] \
            + waypoints[start_way_point_index:end_way_point_index] + \
            [tuple(route[end_projection_index]) + (end_projection_index,)]
    return new_waypoints


def trim_waypoints_list(waypoints, start, end, route):
    print(start)
    start_projection_index = project_point_on_route(start, route)[0]
    end_projection_index = project_point_on_route(end, route)[0]

    return trim_waypoints_index(waypoints, route, start_projection_index, end_projection_index)

#For later use
def get_remaining_route(route, start):
    start_proj_i = project_point_on_route(start, route)[0]
    return route[start_proj_i:]


def get_time_estimation(waypoints, token, mode):
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
    print(response.json())
    return round(response.json()["routes"][0]["duration"] / 60)
  

async def get_vehicle_time_estimation(vehicle_id, dest, token, route_waypoints=None):
    vehicle_location = await db.get_vehicle_location(vehicle_id)
    v_long, v_lat = vehicle_location["longitude"], vehicle_location["latitude"]
    
    route_id = await db.get_vehicle_route_id(vehicle_id)
    route = db.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]
    if route_waypoints is None: 
        route_waypoints = await db.get_route_waypoints(route_id)
    projected_pick_up = route[project_point_on_route(dest,route)[0]]
    rem_waypoints = trim_waypoints_list(route_waypoints, (v_long, v_lat), projected_pick_up, route)
    
    time_estimation = get_time_estimation(rem_waypoints, token, "driving")
    return time_estimation

async def check_vehicle_passed(vehicle_id, dest):
    route_id = await db.get_vehicle_route_id(vehicle_id)
    vehicle_location = await db.get_vehicle_location(vehicle_id)
    v_long, v_lat = vehicle_location["longitude"], vehicle_location["latitude"]
    
    route_coords = db.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]
    vehicle_proj_index = project_point_on_route((v_long, v_lat), route_coords)[0]
    dest_proj_index = project_point_on_route(dest, route_coords)[0]
    
    return vehicle_proj_index >= dest_proj_index

def filter_vehicles__pick_up(pick_up, vehicles, route):
    vehicles = deepcopy(vehicles)
    long, lat = pick_up

    # Project all vehicles on the route
    for vehicle in vehicles:
        projection_index = project_point_on_route((vehicle["longitude"], vehicle["latitude"]), route)[0]
        vehicle["projection_index"] = projection_index
        
    projected_pick_up_point_index = project_point_on_route((long, lat), route)[0]

    vehicles.sort(key=lambda x: x["projection_index"], reverse = True)
    i = 0
    for i, vehicle in enumerate(vehicles):
        if vehicle["projection_index"] <= projected_pick_up_point_index:
            break
    else:
        i += 1
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


def search_routes(query: str, routes_info):
    routes_result = [] 
    filtered_routes_result = []


    for i, element in enumerate(routes_info):
        temp_result = [0, 0] # [score, id]
        temp_score = (process.extract(query, element[1:]))[0][-1]

        if temp_score >=80:
            temp_result[0] = temp_score
            temp_result[1] = routes_info[i][0]
            routes_result.append(temp_result)

        else:
            for j in range (1, len(element)):
                temp_score = fuzz.partial_ratio(query, element[j])
                if temp_score >=80:
                        temp_result[0] = temp_score
                        temp_result[1] = routes_info[i][0]
                        routes_result.append(temp_result)
                        break
                
    print("\n", routes_result, "\n")
    if routes_result != []:
        max_score = max(res[0] for res in routes_result)
        if max_score >=90:
            for res in routes_result:
                if res[0]>=90:      
                    filtered_routes_result.append(res[1])
            
        else:
            for res in routes_result:
                 filtered_routes_result.append(res[1])

    return filtered_routes_result


def search_vehicles(query: str, vehicles_info):
    result = []
    for i, element in enumerate(vehicles_info):
        x = fuzz.partial_ratio(query, element[1])
        y = process.extract(query, (element[1],''))
        print(max(x,y[0][-1]), element)
        if max(x,y[0][-1])>=90:
            result.append(i)

    return result


def off_track(vehicle_id, route, threshold):
    if project_point_on_route(vehicle_id, route)[1] >= threshold:
        return True
    return False

def flatten_route_data(route):
    res: dict = route["details"].copy()
    res["line"]= route["line"]
    return res
    

async def get_nearby_routes_to_1_point(long, lat, radius, routes):
    close_routes = []
    routes_distances = {}
    for route_id, route_data in routes.items():
        route_coords = route_data["line"]["features"][0]["geometry"]["coordinates"]
        min_distance = project_point_on_route((long, lat), route_coords)[1]
        print("checking " + route_data["details"]["route_name"] + "...")
        if min_distance <= radius:
            routes_distances[route_id] = min_distance
            route_vehicles = await db.get_route_vehicles(route_id)
            for vehicle in route_vehicles:
                del vehicle["longitude"]
                del vehicle["latitude"]

            route_id = route_data["details"]["route_id"]
            route_needed_data = {
                         "route_id": route_id,
                         "route_name": route_data["details"]["route_name"],
                         "description": route_data["details"]["description"],
                         "vehicles" : route_vehicles,
                         "line": route_data["line"]
                        }
            close_routes.append(route_needed_data)
    close_routes.sort(key=lambda route: routes_distances[route["route_id"]])
    return close_routes


async def get_nearby_routes_to_2_point(long, lat, radius, long2, lat2, radius2, routes):
    close_routes = []
    routes_distances = {}
    for route_id, route_data in routes.items():
        route_coords = route_data["line"]["features"][0]["geometry"]["coordinates"]
        proj1_index, min_distance = project_point_on_route((long, lat), route_coords)
        proj2_index, min_distance2 = project_point_on_route((long2, lat2), route_coords)
        if proj2_index < proj1_index: continue
        print("checking " + route_data["details"]["route_name"] + "...")
        if min_distance <= radius and min_distance2 <=radius2:
            routes_distances[route_id] = min_distance
            route_vehicles = await db.get_route_vehicles(route_id)
            for vehicle in route_vehicles:
                del vehicle["longitude"]
                del vehicle["latitude"]
                
            route_needed_data = {
                "chain": False,
                "route_id": route_id,
                "route_name": route_data["details"]["route_name"],
                "description": route_data["details"]["description"],
                "eta": 0,
                "vehicles": route_vehicles,
                "line": route_data["line"]
            }
            
            close_routes.append(route_needed_data)
    return close_routes
            


def cascader(intersection_data, all_routes_near_A, all_routes_near_B):
    valid_chains = []
    duplicated_2 = {route[0] for route in all_routes_near_B}
    routes_near_A = [route for route in all_routes_near_A if route[0] not in duplicated_2]
    duplicated_1 = {route[0] for route in all_routes_near_A}
    routes_near_B = [route for route in all_routes_near_B if route[0] not in duplicated_1]

    for A_route_id, pickup_index in routes_near_A:
        for route1_id, route1_inter_proj, route2_id, route2_inter_proj in intersection_data:
            if A_route_id != route1_id: continue
            for B_route_id, dest_index in routes_near_B:
                if route2_id != B_route_id: continue
                if pickup_index > route1_inter_proj or dest_index < route2_inter_proj: continue
                chain = Chain(*map(int, (route1_id, route1_inter_proj, route2_id, route2_inter_proj, pickup_index, dest_index)))
                valid_chains.append(chain)

    return valid_chains


async def nearby_routes(long, lat, radius, routes):
    routes_index = []
    for route_id, route_data in routes.items():
        route_coords = route_data["line"]["features"][0]["geometry"]["coordinates"]
        proj_index, min_distance = project_point_on_route((long, lat), route_coords)
        if min_distance <= radius:
            routes_index.append((route_id, proj_index))
    return (routes_index)

async def filter_duplicate_chains(chains):
    filtered_chains = chains.copy()
    for i, chain1 in enumerate(chains):
        for chain2 in chains[i + 1:]:
            if chain1.route1_id == chain2.route1_id and chain1.route2_id == chain2.route2_id:
                lenght_1 = int(chain2.route1_inter_proj) - chain1.pickup_index + chain1.dest_index - int(chain1.route2_inter_proj)
                lenght_2 = int(chain2.route1_inter_proj) - chain2.pickup_index + chain2.dest_index - int(chain2.route2_inter_proj)
                if lenght_1 < lenght_2:
                    filtered_chains.remove(chain2)
                else:
                    filtered_chains.remove(chain1)
    return filtered_chains

# Chain = namedtuple("route1_id", "route1_inter_proj", "route2_id", "route2_inter_proj", "pickup_index", "dest_index")
async def cascaded_routes(intersections, nearby_A, nearby_B, routes, mapbox_token):
    chains = cascader(intersections, nearby_A, nearby_B)
    filtered_chains: List[Chain] = await filter_duplicate_chains(chains)

    cascaded_output = []
    for i, chain in enumerate(filtered_chains):
        route1_id = chain.route1_id
        waypoints1 = await db.get_route_waypoints(route1_id)

        route_1_coords = routes[route1_id]["line"]["features"][0]["geometry"]["coordinates"]
        trimed_waypoints1 = trim_waypoints_index(waypoints1, route_1_coords, chain.pickup_index, chain.route1_inter_proj)
        eta1 = get_time_estimation(trimed_waypoints1, mapbox_token, "driving")
        vehicles1 = await db.get_route_vehicles(route1_id)
        for vehicle in vehicles1:
            del vehicle["longitude"]
            del vehicle["latitude"]
        sliced_1 = route_1_coords[chain.pickup_index : chain.route1_inter_proj + 1]

        route2_id = chain.route2_id
        waypoints2 = await db.get_route_waypoints(route2_id)
        route_2_coords = routes[route2_id]["line"]["features"][0]["geometry"]["coordinates"]
        trimed_waypoints2 = trim_waypoints_index(waypoints2, route_2_coords, chain.route2_inter_proj, chain.dest_index)
        eta2 = get_time_estimation(trimed_waypoints2, mapbox_token, "driving")
        vehicles2 = await db.get_route_vehicles(route2_id)
        for vehicle in vehicles2:
            del vehicle["longitude"]
            del vehicle["latitude"]
        sliced_2 = route_2_coords[chain.route2_inter_proj : chain.dest_index + 1]
        formated_output = {
            "chain": True,
            "route_id1": route1_id,
            "route_name1": routes[route1_id]["details"]["route_name"],
            "description1": routes[route1_id]["details"]["description"],
            "eta1": eta1,
            "vehicles1": vehicles1,
            "route_id2": route2_id,
            "route_name2": routes[route2_id]["details"]["route_name"],
            "description2": routes[route2_id]["details"]["description"],
            "eta2": eta2,
            "vehicles2": vehicles2,
            "eta": eta1 + eta2,
            "line1": {
              "type": "FeatureCollection",
              "features": [
                {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "coordinates": route_1_coords,
                    "type": "LineString"
                  }
                }
              ]
            },
            "line2": {
              "type": "FeatureCollection",
              "features": [
                {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "coordinates": route_2_coords,
                    "type": "LineString"
                  }
                }
              ]
            },
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
        cascaded_output.append(formated_output)    

    return cascaded_output

async def get_nearby_routes(long, lat, radius, long2, lat2, radius2, routes, mapbox_token):
    intersections = await db.get_intersections()
    nearby_A = await nearby_routes(long, lat, radius, routes)
    nearby_B = await nearby_routes(long2, lat2, radius2, routes)

    not_cascaded_close_routes = await get_nearby_routes_to_2_point(long, lat, radius, long2, lat2, radius2, routes)
    cascaded_close_routes = await cascaded_routes(intersections, nearby_A, nearby_B, routes, mapbox_token)

    total = not_cascaded_close_routes + cascaded_close_routes
    total.sort(key=lambda route: route["eta"])
    return total


def is_valid_email(email: str):
    """Check if email has a valid form

    Parameters:
    - email: string to be validated

    Returns: 
    - True if `email` contains a valid email, False otherwise
    
    """
    email_regex_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    valid_email = re.match(email_regex_pattern, email) is not None
    return valid_email

async def check_email(email: str, account_type: Literal["passenger", "vehicle"]):
    """Check if email has a valid form and is un-used

    Parameters:
    - email: string to be validated

    Returns: 
    - True if `email` contains a valid email that is unused, False otherwise
    
    """
    valid_email = is_valid_email(email)
    is_available_email = await db.check_email_available(email, account_type)
    return valid_email and is_available_email

def is_valid_phone_number(phone_number: str):
    """Check if phone number has a valid form

    Parameters:
    - phone_number: string to be validated

    Returns: 
    - True if `phone_number` contains a valid phone number, False otherwise
    
    """
    phone_number_regex_pattern = r"^\d{8}$"
    valid_phone_number = (re.match(phone_number_regex_pattern, phone_number) is not None)
    return valid_phone_number

async def check_phone_number(phone_number: str, account_type: Literal["passenger", "vehicle"]):
    """Check if phone number has a valid form and is un-used

    Parameters:
    - phone_number: string to be validated

    Returns: 
    - True if `phone_number` contains a valid phone number that is un-used, False otherwise
    
    """
    valid_phone_number = is_valid_phone_number(phone_number)
    is_available_phone_number = await db.check_phone_number_available(phone_number, account_type)
    return valid_phone_number and is_available_phone_number

def is_valid_password(password: str):
    """Check if password has correct form"""
    password_regex_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
    is_valid_password = re.match(password_regex_pattern, password) is not None
    return is_valid_password

