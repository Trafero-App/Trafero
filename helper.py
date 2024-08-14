import math
import requests
from db_layer import db
from dotenv import load_dotenv, find_dotenv
import os
from copy import deepcopy
from fuzzywuzzy import fuzz, process
from collections import namedtuple
from typing import List

Chain = namedtuple("Chain", ["route1_id", "route1_intersection", "route2_id", "route2_intersection", "pickup_index", "dest_index"])

load_dotenv(find_dotenv())

#GENERAL
#GOOD
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

#GOOD
def project_point_on_route(point, route_id):

    route_coords = db.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]
    minimum_distance = float('inf')
    for i,route_point in enumerate(route_coords):
        temp_distance = haversine(point, route_point)
        if temp_distance <= minimum_distance :
            minimum_distance = temp_distance
            closest_point_index = i
    return (closest_point_index, minimum_distance)

###############################################################################################################
#ROUTES 
#For later use
#GOOD
def get_remaining_route(route_id, start):
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

###############################################################################################################
#SEARCH

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
    # print("\n", routes_result, "\n")
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
        # print(max(x,y[0][-1]), element)
        if max(x,y[0][-1])>=90:
            result.append(i)

    return result

###############################################################################################################
#WAYPOINTS AND ETA

#GOOD
async def get_eta(route_id, start_index, end_index, mapbox_token):
    waypoints = await db.get_route_waypoints(route_id)
    trimed_waypoints = trim_waypoints_index(waypoints, route_id, start_index, end_index)
    eta = get_time_estimation(trimed_waypoints, mapbox_token, "driving")
    return eta


#GOOD
def trim_waypoints_index(waypoints, route_id, start_index, end_index):
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

#GOOD
def trim_waypoints_list(waypoints, start, end, route_id):
    # print(start)
    start_index = project_point_on_route(start, route_id)[0]
    end_index = project_point_on_route(end, route_id)[0]

    return trim_waypoints_index(waypoints, route_id, start_index, end_index)

         
#GOOD
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
    # print(response.json())
    return round(response.json()["routes"][0]["duration"] / 60)

###############################################################################################################
# VEHICLES
#GOOD
def off_track(vehicle_id, route_id, threshold):
    route = db.routes[route_id]["line"]["features"][0]["geometry"]["coordinates"]
    if project_point_on_route(vehicle_id, route)[1] >= threshold:
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

###############################################################################################################
# NEARBY ROUTES

#GOOD
def nearby_routes(long, lat, radius, turn_to_dict=False):
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
    routes = nearby_routes(long, lat, radius)
    formated_nearby_routes = []
    for route_id, _ in routes:
        route_output_data = await get_route_data(route_id)
        formated_nearby_routes.append(route_output_data)
    return formated_nearby_routes

#GOOD
async def get_nearby_routes_to_2_point(long, lat, radius, long2, lat2, radius2, mapbox_token):
    routes = []
    routes_A = nearby_routes(long, lat, radius, True)
    routes_B = nearby_routes(long2, lat2, radius2, True)

    for route_id in routes_A:
        if route_id not in routes_B: continue
        start_index = routes_A[route_id] 
        end_index = routes_B[route_id]
        if end_index < start_index: continue        
        route_data = await get_route_data(route_id)
        eta = await get_eta(route_id, start_index, end_index, mapbox_token)
        route_data["chain"] = False
        route_data["eta"] = eta           
        routes.append(route_data)

    return routes




#GOOD
def chainer(intersection_data, routes_A, routes_B):
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
    chains = chainer(intersections, nearby_A, nearby_B)
    filtered_chains: List[Chain] = await filter_duplicate_chains(chains)
    chained_output = []

    for i, chain in enumerate(filtered_chains):

        route1_id = chain.route1_id
        route1_data = await get_route_data(route1_id, 1)
        eta1 = await get_eta(route1_id, chain.pickup_index, chain.route1_intersection, mapbox_token)
        sliced_1 = route1_data["line1"]["features"][0]["geometry"]["coordinates"][chain.pickup_index : chain.route1_intersection + 1]
        route1_data["eta1"] = eta1

        route2_id = chain.route2_id
        route2_data = await get_route_data(route2_id, 2)
        eta2 = await get_eta(route2_id, chain.route2_intersection, chain.dest_index, mapbox_token)
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
    intersections = await db.get_intersections()
    nearby_A = nearby_routes(long, lat, radius, mapbox_token)
    nearby_B = nearby_routes(long2, lat2, radius2, mapbox_token)

    close_routes = await get_nearby_routes_to_2_point(long, lat, radius, long2, lat2, radius2, mapbox_token)
    chained_close_routes = await chained_routes(intersections, nearby_A, nearby_B, mapbox_token)

    total = close_routes + chained_close_routes
    total.sort(key=lambda route: route["eta"])
    return total