import math

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




def get_time_estimation(start, end, way_points):
    if start[2] == end[2]:
        return 0
    
    if (start[0],start[1]) == (way_points[0][0], way_points[0][1]):
            start_way_point_index = 0
    else:
        for i, way_point in enumerate(way_points):
            if way_point[2] > start[3]:
                start_way_point_index = i
                break

    if (end[0],end[1]) == (way_points[-1][0], way_points[-1][1]):
            end_way_point_index = len(way_points)-1
    else:
        for i, way_point in enumerate(way_points):
            if way_point[2] >= end[2]:
                end_way_point_index = i
                break
    
    way_points = [(start[0],start[1])] + way_points[start_way_point_index:end_way_point_index] + [(end[0],end[1])]