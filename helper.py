import math
import requests

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
                                 "vehicle_id": vehicle["vehicle_id"]
                                },
                            "geometry": {
                                 "type": "Point",
                                 "coordinates": [
                                      vehicle["longitude"],
                                      vehicle["latitude"]
                                 ] 
                            } }
         
def get_time_estimation(waypoints, api_key):
    url = "https://api.mapbox.com/directions/v5/mapbox/driving-traffic/" + \
    ';'.join([",".join(map(str, x[:2])) for x in waypoints])
    url += "?alternatives=false" # Don't search for alternative routes
    url += "&continue_straight=true" # Tend to continue in the same direction
    url += "&steps=false" # Don't include turn-by-turn instrutions
    params = {'access_token': api_key,
              'geometries': 'geojson',
              'overview': 'full'
              }
    response = requests.get(url, params=params)
    return response.json()["routes"][0]["duration"]
