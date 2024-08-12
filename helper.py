import math
import requests
from db_layer import db
from dotenv import load_dotenv, find_dotenv
import os
from copy import deepcopy
from fuzzywuzzy import fuzz, process
import json
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

def off_track(vehicle_id, route, threshold):
    if project_point_on_route(vehicle_id, route)[1] >= threshold:
        return True
    return False






async def eta(route_id:int, long1:float, lat1:float, long2:float, lat2:float, routes):
    # Load route
    route = routes[route_id]["line"]["geometry"]["coordinates"]
    waypoints = await db.get_route_waypoints(route_id)
    waypoints = trim_waypoints_list(waypoints, (long1, lat1), (long2, lat2), route)
    return get_time_estimation(waypoints, "pk.eyJ1IjoibWFyY2FzMTIzIiwiYSI6ImNseTY5Mmh1czA4YXAybHNhNGRibmh5MmoifQ.n-2d-SQkNvAkjZAoVQNcsA", "driving")






async def get_nearby_routes_to_1_point(long, lat, radius, routes):
    close_routes = []
    routes_distances = {}
    for route_id, route_data in routes.items():
        template = {
                    "route_id": 0,
                    "route_name": "",
                    "description": "",
                    "vehicles": [],
                    "line": {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "properties": {},
                                "geometry": {
                                "coordinates": [],
                                "type": "LineString"
                                }
                            }
                        ]
                      } 
                    }
        route_coords = route_data["line"]["geometry"]["coordinates"]
        min_distance = project_point_on_route((long, lat), route_coords)[1]
        print("checking " + route_data["details"]["route_name"] + "...")
        if min_distance <= radius:
            routes_distances[route_id] = min_distance
            route_vehicles = await db.get_route_vehicles(route_id)
            for vehicle in route_vehicles:
                del vehicle["longitude"]
                del vehicle["latitude"]
            route_data["vehicles"] = route_vehicles

            route_id = route_data["details"]["route_id"]
            route_name = route_data["details"]["route_name"]
            description = route_data["details"]["description"]
            vehicles = route_data["vehicles"]
            line = route_data["line"]["geometry"]["coordinates"]
            template["route_id"] = route_id
            template["route_name"] = route_name
            template["description"] = description
            template["vehicles"] = vehicles
            template["line"]["features"][0]["geometry"]["coordinates"] = line

            close_routes.append(template)
    # close_routes.sort(key=lambda route: routes_distances[route["details"]["route_id"]])
    return close_routes


async def get_nearby_routes_to_2_point(long, lat, radius, long2, lat2, radius2, routes):
    close_routes = []
    routes_distances = {}
    for route_id, route_data in routes.items():
        template = {
                    "chain": False,
                    "route_id": 0,
                    "route_name": "",
                    "description": "",
                    "vehicles": [],
                    "eta": 0,
                    "line": {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "properties": {},
                                "geometry": {
                                "coordinates": [],
                                "type": "LineString"
                                }
                            }
                        ]
                      } 
                    }
        route_data["chain"] = False
        route_coords = route_data["line"]["geometry"]["coordinates"]
        min_distance = project_point_on_route((long, lat), route_coords)[1]
        min_distance2 = project_point_on_route((long2, lat2), route_coords)[1]
        print("checking " + route_data["details"]["route_name"] + "...")
        if min_distance <= radius and min_distance2 <=radius2:
            routes_distances[route_id] = min_distance
            route_vehicles = await db.get_route_vehicles(route_id)
            for vehicle in route_vehicles:
                del vehicle["longitude"]
                del vehicle["latitude"]
            route_data["vehicles"] = route_vehicles


            route_id = route_data["details"]["route_id"]
            route_name = route_data["details"]["route_name"]
            description = route_data["details"]["description"]
            vehicles = route_data["vehicles"]
            line = route_data["line"]["geometry"]["coordinates"]
            template["route_id"] = route_id
            template["route_name"] = route_name
            template["description"] = description
            template["vehicles"] = vehicles
            template["line"]["features"][0]["geometry"]["coordinates"] = line
            template["eta"] = 10
            close_routes.append(template)
            # close_routes.sort(key=lambda route: routes_distances[route["details"]["route_id"]])
    return close_routes
            

def flatten_route_data(route):
    res: dict = route["details"].copy()
    res["line"] = route["line"]
    return res
    


def cascader(all_info, routes_near_A, routes_near_B):
    intersections = []
    filtered = []
    for x in routes_near_A:
        for info in all_info:
            if info[0] == x[0]:
                for y in routes_near_B:
                    if info[2] == y[0]:
                        intersections.append(info+(x[1],)+(y[1],))
    if intersections == []:
        return "NO AVAILABLE ROUTES"
    else:
        for i in range (len(intersections)):
            for route in routes_near_A:
                if intersections[i][0] == route[0]:
                    if intersections[i][1] > route[1]:
                        intersections[i] = intersections[i] + (True,)
                    else:
                        intersections[i] = intersections[i] + (False,)
        for i in range (len(intersections)):
            for route in routes_near_B:
                if intersections[i][2] == route[0]:
                    if intersections[i][-1] == True:
                        if intersections[i][3] > route[1]:
                            intersections[i] = intersections[i][:-1] + (False,)
        for element in intersections:
            if element[-1] == True:
                filtered.append(element[:-1])

        return filtered




async def nearby_routes(long, lat, radius, routes):
    routes_index = []
    for route_id, route_data in routes.items():
        route_coords = route_data["line"]["geometry"]["coordinates"]
        point_index = project_point_on_route((long, lat), route_coords)[0]
        min_distance = project_point_on_route((long, lat), route_coords)[1]
        if min_distance <= radius:
            routes_index.append((route_id, point_index))
    return (routes_index)




async def cascaded_routes(intersections, nearby_A, nearby_B, routes):
    combinations = cascader(intersections, nearby_A, nearby_B)
    filtered_combinations = combinations.copy()
    for i in range(len(combinations)):
        for j in range(i+1, len(combinations)):
            if combinations[i][0] == combinations[j][0] and combinations[i][2] == combinations[j][2]:
                lenght_1 = int(combinations[i][1]) - combinations[i][4] + combinations[i][5] - int(combinations[i][3])
                lenght_2 = int(combinations[j][1]) - combinations[j][4] + combinations[j][5] - int(combinations[j][3])
                if lenght_1 < lenght_2:
                    filtered_combinations.remove(combinations[j])
                else:
                    filtered_combinations.remove(combinations[i])
            
    cascaded_output = []
    print('\n\n\n\n\n',combinations,'\n\n\n')
    print(filtered_combinations,'\n\n\n\n\n')
    for i, result in enumerate(filtered_combinations):
        template = {
            "chain": True,
            "route_id1": 0,
            "route_name1": "",
            "description1": "",
            "vehicles1": [],
            "eta1": 0,
            "route_id2": 0,
            "route_name2": "",
            "description2": "",
            "vehicles2": [],
            "eta2": 0,
            "line1": {
                "type": "FeatureCollection",
                "features": [
                  {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                      "coordinates": [],
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
                      "coordinates": [],
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
                    "coordinates": [],
                    "type": "LineString"
                  }
                },
                {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "coordinates": [],
                    "type": "LineString"
                  },
                  "id": 1
                }
              ]
            }
      }
        route_id1 = result[0]
        p1 = result[4]
        p2 = int(result[1])
        route_id2 = result[2]
        p3 = int(result[3])
        p4 = result[5]

        route_name1 = routes[route_id1]["details"]["route_name"]
        description1 = routes[route_id1]["details"]["description"]
        vehicles1 = await db.get_route_vehicles(route_id1)
        for vehicle in vehicles1:
            del vehicle["longitude"]
            del vehicle["latitude"]
        route_name2 = routes[route_id2]["details"]["route_name"]
        description2 = routes[route_id2]["details"]["description"]
        vehicles2 = await db.get_route_vehicles(route_id2)
        for vehicle in vehicles2:
            del vehicle["longitude"]
            del vehicle["latitude"]
        line_1 = routes[route_id1]["line"]["geometry"]["coordinates"]
        line_2 = routes[route_id2]["line"]["geometry"]["coordinates"]
        sliced_1 = line_1[p1:p2+1]
        sliced_2 = line_2[p3:p4+1]


        template["route_id1"] = route_id1
        template["route_name1"] = route_name1
        template["description1"] = description1
        template["vehicles1"] = vehicles1
        template["eta1"] = 15
        template["route_id2"] = route_id2
        template["route_name2"] = route_name2
        template["description2"] = description2
        template["vehicles2"] = vehicles2
        template["eta2"] = 20
        template["line1"]["features"][0]["geometry"]["coordinates"] = line_1
        template["line2"]["features"][0]["geometry"]["coordinates"] = line_2
        template["line"]["features"][0]["geometry"]["coordinates"] = sliced_1
        template["line"]["features"][1]["geometry"]["coordinates"] = sliced_2
        cascaded_output.append(template)    

    return cascaded_output

async def nearby(long, lat, radius, long2, lat2, radius2, routes):
    intersections = await db.get_intersections()
    nearby_A = await nearby_routes(long, lat, radius, routes)
    nearby_B = await nearby_routes(long2, lat2, radius2, routes)

    not_cascaded_close_routes = await get_nearby_routes_to_2_point(long, lat, radius, long2, lat2, radius2, routes)
    cascaded_close_routes = await cascaded_routes(intersections, nearby_A, nearby_B, routes)

    
    return not_cascaded_close_routes + cascaded_close_routes



