"""
search.py

This module handles all functions related to searching.

"""

from fuzzywuzzy import fuzz, process
from database import db


def search_routes(query: str):
    """Get routes based on a query

    Parameters:
    - Query: the word the user is searching for
    - All routes information

    Returns:
    - All routes related to the query
    """
    # Get all matching routes
    route_scores = {}
    routes_search_data = db.routes_search_data
    for route_search_data in routes_search_data:
        score1 = (process.extract(query, route_search_data[1:]))[0][-1]
        score2 = max(
            fuzz.partial_ratio(query, route_search_data)
            for route_search_data in routes_search_data
        )

        score = max(score1, score2)
        if score >= 80:
            route_scores[route_search_data[0]] = score

    filtered_routes_result = {}
    # If some routes have a high score, ignore ones with a low score
    if route_scores != {}:
        max_score = max(route_scores.values())
        if max_score >= 90:
            for route_id, score in route_scores.items():
                if score >= 90:
                    filtered_routes_result[route_id] = score
        else:
            filtered_routes_result = route_scores
    print(filtered_routes_result)
    filtered_routes_result = sorted(
        filtered_routes_result.keys(), key=filtered_routes_result.get, reverse=True
    )
    print(filtered_routes_result)
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
        score1 = fuzz.partial_ratio(query, element[1])
        score2 = process.extract(query, (element[1], ""))[0][-1]
        score = max(score1, score2)
        if score >= 90:
            result.append(i)
    return result
