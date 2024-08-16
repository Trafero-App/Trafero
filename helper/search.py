"""
search.py

This module handles all functions related to searching.

"""
from fuzzywuzzy import fuzz, process
#SEARCH

def search_routes(query: str, routes_info):
    """Get routes based on a query

    Parameters:
    - Query: the word the user is searching for
    - All routes information

    Returns:
    - All routes related to the query
    """
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
    """Get vehicles based on a search query

    Parameters:
    - Query: license plate 
    - All vehicles info
    Returns:
    - Vehicle that holds the license plate
    """
    result = []
    for i, element in enumerate(vehicles_info):
        x = fuzz.partial_ratio(query, element[1])
        y = process.extract(query, (element[1],''))
        # print(max(x,y[0][-1]), element)
        if max(x,y[0][-1])>=90:
            result.append(i)

    return result