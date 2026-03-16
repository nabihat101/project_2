""" CSC111 Project 2

Module Description
==================
This file contains all the methods used to calculate probability of two species interacting and to calculate distance between two locations (longitude and latitude) 

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 by Nabiha Tariq, Yusyra Hossain, Eleanor Neal, Ruoshui Deng
"""


def calculate_interaction_likelihood(co_occurrences: int, obs_a: int, obs_b: int) -> float:
    """
    Calculates the likelihood of interaction between two species using the Jaccard Index.

    Args:
        co_occurrences: The number of times the two species were observed
                        within your proximity/time thresholds.
        obs_a: Total number of observations for Species A in that season.
        obs_b: Total number of observations for Species B in that season.

    Returns:
        A float between 0.0 (never interact) and 1.0 (always interact).
    """
    if obs_a == 0 and obs_b == 0:
        return 0.0
    else:
        total_unique_observations = (obs_a + obs_b) - co_occurrences
        likelihood = co_occurrences / total_unique_observations
        return likelihood


def haversine_distance_km(loc1: tuple[float, float], loc2: tuple[float, float]) -> float:
    """Calculates distance in kilometers between two (lat, lon) points using the Haversine formula."""
    import math

    # create latitude and longtidue coordinates from the tuples
    lat1, lon1 = loc1
    lat2, lon2 = loc2

    # account for earth's curvature 
    radius_km = 6371.0

    # convert into radians 
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    # difference in latitudes
    d_phi = math.radians(lat2 - lat1)

    # difference in longitudes 
    d_lambda = math.radians(lon2 - lon1)

    # apply haversine formula
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return radius_km * c

# import python_ta
   # python_ta.check_all(config={
    #'extra-imports': ['pandas', 'networkx'],  # the names (strs) of imported modules
    #'allowed-io': [],     # the names (strs) of functions that call print/open/input
    #'max-line-length': 120
#})
