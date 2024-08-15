import requests
from db_layer import db
from operations import project_point_on_route 


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