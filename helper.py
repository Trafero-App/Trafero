import math
import requests
from db_layer import db
from dotenv import load_dotenv, find_dotenv
import os
from copy import deepcopy
from fuzzywuzzy import fuzz, process
import json

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


def geojsonify_vehicle_list(vehicle_list):
    for i, vehicle in enumerate(vehicle_list):
        vehicle_list[i] = {
                            "type": "Feature", 
                            "properties": {
                                 "vehicle_id": vehicle["vehicle_id"],
                                 "status": vehicle["status"]
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

def filter_vehicles__pick_up(pick_up, vehicles, route):
    print("EDFI")
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


def search(word: str, routes_info: list, sliced_info: list, busses_info: list):
    output = {} #output dictionary
    routes_result = [] 
    busses_result = []
    filtered_routes_result = []

    
    #This list takes tuples of the form (id, route_name, description) from TABLE route
    routes_info = [
            (1,'Bus 15 (Dawra - Nahr al Mot)', 'Dawra - Port - Biel - Ain el Mrayse - Raouche - Unesco - Cola - Corniche el Mazraa - Barbir - Mathaf - Adliye - Souk el Ahad - Nahr el Mot'), 
            (2,'Bus 15 (Nahr al Mot - Dawra)', 'Nahr al Mot - Souk el Ahad - Adliye - Mathaf - Barbir - Corniche el Mazraa - Cola - Unesco - Raouche - Ain el Mrayse - Biel - Port - Dawra'), 
            (3,'Van Saida (Beirut - Saida)', 'Cola - Madine al Riyadiye - Airport Highway - Khalde - Doha - Nahmeh - Damour - Jiye - Jadra - Saida (sehit nejme)'), 
            (4,'Van Saida (Saida - Beirut)', 'Saida (Sehit Nejme) - Jadra - Jiye - Damour - Nahmeh - Doha - Khalde - Airport Highway - Madine al Riyadiye - Cola'), 
            (5,'Van 4 (Hamra - Hay el Selom)', 'Hamra - Spears - Bechara el Khoury - Horsh Beirut - Old Saida Road - Haret Hreik - Hadath - Lailake - Hay el Selom'), 
            (6,'Van 4 (Hay el Selom - Hamra)', 'Hay el Selom - Lailake - Hadath - Haret Hreik - Old Saida Road - Horsh Beirut - Bechara el Khoury - Spears - Hamra'), 
            (7,'Van (Ain el Mrayse - Jesr al Matar)', 'Ain el Mrayse - Manara - Raouche - Unesco - Jnah - Bir Hassan - Rihab - Jesr al Matar'), 
            (8,'Van (Jesr al Matar - Ain el Mrayse)', 'Jesr al Matar - Rihab - Bir Hassan - Jnah - Unesco - Raouche - Manara - Ain el Mrayse'), 
            (9,'Bus 2 (Hamra - Antelias)', 'Hamra - Tallet al Drouz - Mar Elias - Basta al Tahta - Achrafiye - Karantina - Borj Hammoud - Baouchriyeh - Jdeideh - Zalqa - Jal el Dib - Antelias'), 
            (10,'Bus 2 (Antelias - Hamra)', 'Antelias - Jal el Dib - Zalqa - Jdeideh - Baouchriyeh - Borj Hammoud - Karantina - Achrafiye - Basta al Tahta - Mar Elias - Tallet al Drouz - Hamra'), 
            (11,'Van 10 (Dawra - Matar)', 'Dawra - Port - Bechara el Khoury - Horsh beirut - Borj al Barajne - Tohwitet el Ghadir - Airport'), 
            (12,'Van 10 (Matar - Dawra)', 'Airport - Tohwitet el Ghadir - Borj al Barajne - Horsh Beirut - Bechara el Khoury - Port - Dawra'), 
            (13,'Bus 24 (Hamra - Badaro)', 'Hamra - Verdun - Corniche el Mazraa - Mathaf - Adliye - Badaro'), 
            (14,'Bus 24 (Badaro - Hamra)', 'Badaro - Adliye - Mathaf - Corniche el Mazraa - Verdun - Hamra') 
        ]
    
    #This list takes tuples containing sliced str from above list
    sliced_info = [
        (1, 'Bus 15', 'Dawra', 'Nahr al Mot', 'Dawra', 'Port', 'Biel', 'Ain el Mrayse', 'Raouche', 'Unesco', 'Cola', 'Corniche el Mazraa', 'Barbir', 'Mathaf', 'Adliye', 'Souk el Ahad', 'Nahr el Mot'),
        (2, 'Bus 15', 'Nahr al Mot', 'Dawra', 'Nahr al Mot', 'Souk el Ahad', 'Adliye', 'Mathaf', 'Barbir', 'Corniche el Mazraa', 'Cola', 'Unesco', 'Raouche', 'Ain el Mrayse', 'Biel', 'Port', 'Dawra'),
        (3, 'Van Saida', 'Beirut', 'Saida', 'Cola', 'Madine al Riyadiye', 'Airport Highway', 'Khalde', 'Doha', 'Nahmeh', 'Damour', 'Jiye', 'Jadra', 'Saida', 'sehit nejme'),
        (4, 'Van Saida', 'Saida', 'Sehit', 'Nejme', 'Jadra', 'Jiye', 'Damour', 'Nahmeh', 'Doha', 'Khalde', 'Airport Highway', 'Madine al Riyadiye', 'Cola'),
        (5, 'Van 4', 'Hamra', 'Hay el Selom', 'Hamra', 'Spears', 'Bechara el Khoury', 'Horsh Beirut', 'Old Saida Road', 'Haret Hreik', 'Hadath', 'Lailake', 'Hay el Selom'),
        (6, 'Van 4', 'Hay el Selom', 'Hamra', 'Hay el Selom', 'Lailake', 'Hadath', 'Haret Hreik', 'Old Saida Road', 'Horsh Beirut', 'Bechara el Khoury', 'Spears', 'Hamra'),
        (7, 'Van Bahre', 'Ain el Mrayse', 'Jesr al Matar', 'Ain el Mrayse', 'Manara', 'Raouche', 'Unesco', 'Jnah', 'Bir Hassan', 'Rihab', 'Jesr al Matar'),
        (8, 'Van Bahre', 'Jesr al Matar', 'Ain el Mrayse', 'Jesr al Matar', 'Rihab', 'Bir Hassan', 'Jnah', 'Unesco', 'Raouche', 'Manara', 'Ain el Mrayse'),
        (9, 'Bus 2', 'Hamra', 'Antelias', 'Hamra', 'Tallet al Drouz', 'Mar Elias', 'Basta al Tahta', 'Achrafiye', 'Karantina', 'Borj Hammoud', 'Baouchriyeh', 'Jdeideh', 'Zalqa', 'Jal el Dib', 'Antelias'),
        (10, 'Bus 2', 'Antelias', 'Hamra', 'Antelias', 'Jal el Dib', 'Zalqa', 'Jdeideh', 'Baouchriyeh', 'Borj Hammoud', 'Karantina', 'Achrafiye', 'Basta al Tahta', 'Mar Elias', 'Tallet al Drouz', 'Hamra'),
        (11, 'Van 10', 'Dawra', 'Matar', 'Dawra', 'Port', 'Bechara el Khoury', 'Horsh Beirut', 'Borj al Barajne', 'Tohwitet el Ghadir', 'Airport'),
        (12, 'Van 10', 'Matar', 'Dawra', 'Airport', 'Tohwitet el Ghadir', 'Borj al Barajne', 'Horsh Beirut', 'Bechara el Khoury', 'Port', 'Dawra'),
        (13, 'Bus 24', 'Hamra', 'Badaro', 'Hamra', 'Verdun', 'Corniche el Mazraa', 'Mathaf', 'Adliye', 'Badaro'),
        (14, 'Bus 24', 'Badaro', 'Hamra', 'Badaro', 'Adliye', 'Mathaf', 'Corniche el Mazraa', 'Verdun', 'Hamra')
    ]

    #This list takes tuples of the form (id, license_plate, status) from TABLE vehicle
    busses_info =  [ (2, 'A 111112', 'active'), (2, 'B 111113', 'active'), (2, 'N 11114', 'unavailable'), (1, 'T 11115', 'out of service zone'), (1, 'Z 111116', 'active') ]


    for i, element in enumerate(sliced_info):
        temp_result = ['score', {"route_id": 0, "route_name": "", "description": ""}]
        temp_score = (process.extract(word, element[1:]))[0][-1]

        if temp_score >=80:
            temp_result[0] = temp_score
            temp_result[1]["route_id"] = routes_info[i][0]
            temp_result[1]["route_name"] = routes_info[i][1]
            temp_result[1]["description"] = routes_info[i][2]
            routes_result.append(temp_result)

        else:
            for j in range (1, len(element)):
                temp_score = fuzz.partial_ratio(word, element[j])
                if temp_score >=80:
                        temp_result[0] = temp_score
                        temp_result[1]["route_id"] = routes_info[i][0]
                        temp_result[1]["route_name"] = routes_info[i][1]
                        temp_result[1]["description"] = routes_info[i][2]
                        routes_result.append(temp_result)
                        break
                
    if routes_result != []:
        max_score = max(res[0] for res in routes_result)
        if max_score >=90:
            for res in routes_result:
                if res[0]>=90:      
                    filtered_routes_result.append(res[1])
            output["routes"] = filtered_routes_result
            
        else:
            for res in routes_result:
                 filtered_routes_result.append(res[1])
            output["routes"] = filtered_routes_result


    for element in busses_info:
        tempo_result = {"id": 0, "license_plate": "", "status": ""}
        x = fuzz.partial_ratio(word, element[1])
        y = process.extract(word, (element[1],''))
        if max(x,y[0][-1])>=90:
                tempo_result["id"] = element[0]
                tempo_result["license_plate"] = element[1]
                tempo_result["status"] = element[2]
                busses_result.append(tempo_result)

    if busses_result != []:
        output["busses"] = busses_result

    output_json = json.dumps(output, indent=2) #trun output into json format
    return (output_json)
