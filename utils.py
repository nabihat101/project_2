""" CSC111 Project 2

Module Description ================== This file contains all the methods used to calculate probability of two species
interacting and to calculate distance between two locations (longitude and latitude)

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 by Nabiha Tariq, Yusyra Hossain, Eleanor Neal, Ruoshui Deng
"""
import numpy as np
import pandas as pd


def calculate_interaction_likelihood(co_occurrences: int, obs_a: int, obs_b: int) -> float:
    """
    Calculates the likelihood of interaction between two species using the Jaccard Index. Returns a float between 0.0
    (never interact) and 1.0 (always interact).

    We say that two species are more likely to interact when they are closer to each other.

    Special notes on implementation:
        co_occurrences: The number of times the two species were observed
                        within your proximity/time thresholds.
        obs_a: Total number of observations for Species A in that season.
        obs_b: Total number of observations for Species B in that season.
    """
    if obs_a == 0 and obs_b == 0:
        return 0.0
    else:
        total_unique_observations = (obs_a + obs_b) - co_occurrences
        likelihood = co_occurrences / total_unique_observations
        return round(likelihood, 2)


def get_interaction_parameters(locs_a: list[tuple[str, float, float]],
                               locs_b: list[tuple[str, float, float]],
                               max_distance_km: float) -> tuple[int, int, int]:
    """Finds the co-occurrences, obs_A, and obs_B for two species in a specific season."""
    obs_a_count = len(locs_a)
    obs_b_count = len(locs_b)

    if obs_a_count == 0 or obs_b_count == 0:
        return 0, obs_a_count, obs_b_count

    # Count how many sightings of A have at least one B nearby on the same day
    a_near_b = 0
    for date_a, lat_a, lon_a in locs_a:
        for date_b, lat_b, lon_b in locs_b:
            if date_a[:4] == date_b[:4]:  # Fixed: Checks the year!
                dist = haversine_distance_km((lat_a, lon_a), (lat_b, lon_b))
                if dist <= max_distance_km:
                    a_near_b += 1
                    break

    # Count how many sightings of B have at least one A nearby on the same day
    b_near_a = 0
    for date_b, lat_b, lon_b in locs_b:
        for date_a, lat_a, lon_a in locs_a:
            if date_b[:4] == date_a[:4]:  # Fixed: Checks the year!
                dist = haversine_distance_km((lat_b, lon_b), (lat_a, lon_a))
                if dist <= max_distance_km:
                    b_near_a += 1
                    break

    co_occurrences = min(a_near_b, b_near_a)

    return co_occurrences, obs_a_count, obs_b_count


def haversine_distance_km(loc1: tuple[float, float], loc2: tuple[float, float]) -> float:
    """Calculates distance in kilometers between two (lat, lon) points using the Haversine formula.
     >>> haversine_distance_km((40.7, -70.8), (51.3, 0.18))
    5386.3

    >>> haversine_distance_km((40.7128, -74.0060), (34.0522, -118.2437))
    3935.7
    """
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


def make_circular(img: np.ndarray) -> np.ndarray:
    """
    Return a circular image
    Assume img is a np.ndarray which is an array that holds all the pixels
    """

    # img.shape returns (height, width, channels) but we only need height and width so we split
    h, w = img.shape[:2]

    # find center which is half the width and height and is a corrdinate
    center = (int(w / 2), int(h / 2))

    # find the radius which is the minimum of center tuple
    radius = min(center[0], center[1])

    # create a coordinate grid using numpy (lowercase to satisfy PythonTA)
    y, x = np.ogrid[:h, :w]

    # find distance from center using distance formula
    dist_from_center = (x - center[0]) ** 2 + (y - center[1]) ** 2

    # true/false variable to ensure that distance is less than diameter
    mask = dist_from_center <= radius ** 2

    # ensure that img.shape[2] has rgb colours
    if img.shape[2] == 3:
        # creates a grid of 255's. 255 means it's visible and 0 means it's invisible (the pixel)
        alpha = np.ones((h, w), dtype=np.uint8) * 255

        # stack the alpha onto the image to become rgba
        img = np.dstack((img, alpha))

    # apply mask (outside circle = transparent) and the 3 is the alpha stack we added previously

    img[~mask, 3] = 0

    return img


def get_all_species(data_file: str) -> list[str]:
    """Returns a list of every species in the dataset, used for the species
    dropdown menu in entities.py
    
    Preconditions:
        - data_file is a valid file path to a csv file in the format written by
          the clean_data function
    """

    df = pd.read_csv(data_file)
    return list(df['species_guess'].unique())

# import python_ta
# python_ta.check_all(config={
# 'extra-imports': ['pandas', 'networkx'],  # the names (strs) of imported modules
# 'allowed-io': [],     # the names (strs) of functions that call print/open/input
# 'max-line-length': 120
# })
