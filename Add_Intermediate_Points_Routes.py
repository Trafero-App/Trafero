#### THIS CODE IS TO MINIMIZE THE DISTANCE BETWEEN THE POINTS AND CREATE A NEW GEOJSON FILE OF THE ROUTE  ###


L = [] #DEFINE THE OLD LIST OF POINTS
n = len(L)

##################################             FUNCTIONS             #########################################

import math

def haversine(lon1, lat1, lon2, lat2):
    R = 6371000  # Radius of the Earth in meters
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance

def interpolate_points(lon1, lat1, lon2, lat2, num_points):
    points = []
    for i in range(1, num_points + 1):
        frac = i / (num_points + 1)
        lon = lon1 + frac * (lon2 - lon1)
        lat = lat1 + frac * (lat2 - lat1)
        points.append((lon, lat))
    return points

##################################   WRITING THE NEW LIST OF POINTS   ########################################

segment_length = 10  #DEFINE HOW MUC IS THE DISTANCE YOU WANT
L1 = []              #THE NEW LIST

for i in range (n-1):
    L1.append(L[i])
    lon1, lat1 = L[i]  # Point A (longitude, latitude)
    lon2, lat2 = L[i+1]  # Point B (longitude, latitude)

    # Calculate total distance between A and B
    total_distance = haversine(lon1, lat1, lon2, lat2)
    if total_distance <=15:
        pass

    # Determine the number of intermediate points
    max_distance = total_distance - (total_distance % segment_length)
    num_points = int(max_distance / segment_length)

    # Generate intermediate points
    intermediate_points = interpolate_points(lon1, lat1, lon2, lat2, num_points)
    for i, point in enumerate(intermediate_points, start=1):
        L1.append(point)


###################################         PRINTING OUT THE FILE          ###################################


New_List = [str(sublist) for sublist in L1]
S1 = '{"coordinates": [ ' + ', '.join(New_List) + ' ], "type":"LineString"}'
S2 = ''
for i in S1 :
    if i == '(':
        S2 += '['
    elif i ==')':
        S2 += ']'
    else:
        S2 += i

file_path = input('Enter the route number + version: ')  #Specify the route number here
with open(file_path, 'w') as file:
    file.write(S2)

print('DONE')