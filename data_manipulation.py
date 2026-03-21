"""CSC111 Project 2

Module Description
==================
This module contains the handling data functions used to clean and manipulate a csv data file.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 by Nabiha Tariq, Yusyra Hossain, Eleanor Neal, Ruoshui Deng
"""

import pandas as pd

from entities import Graph, Observation

def clean_data(data_file: str) -> None:
    """
    Creates a datamap using pandas library to clean and filter data based on conditions
    """
    df = pd.read_csv(data_file)
    df_new = df.drop(columns=["id", "uuid", "observed_on_string", "time_observed_at", "time_zone", "user_id", "user_login", "user_name", "created_at", "updated_at", "quality_grade", "url", "image_url", "sound_url", "tag_list", "description", "num_identification_agreements", "num_identification_disagreements", "captive_cultivated", "oauth_application_id", "private_place_guess", "private_latitude", "private_longitude","public_positional_accuracy", "geoprivacy", "taxon_geoprivacy", "coordinates_obscured", "positioning_method", "positioning_device", "scientific_name", "iconic_taxon_name", "taxon_id", "common_name"])
    df_new = df_new[df_new["positional_accuracy"] <= 1000]
    df_new.to_csv("new_file.csv", index=False)


def data_handle(file: str) -> list[Observation]:
    """Reads the data from the csv file and creates a list of Observation objects, 
    each representing a species and its observed locations in different seasons.
    
    Preconditions:
        - all entries in the "observed_on" column of the csv file are in the format "MM/DD/YYYY
        - all entries in the "latitude" and "longitude" columns of the csv file are valid floats """

    df = pd.read_csv(file)
    grouped = df.groupby("species_guess")

    observations = []

    for species, group in grouped:
        obs = Observation(species)

        dates = list(group["observed_on"])
        lats = list(group["latitude"])
        long = list(group["longitude"])

        for x in range(len(dates)):
            curr = dates[x].split("-")[1]

            season = 0
            # Winter is first season
            if int(curr) in [12, 1, 2]:
                season = 1
            elif int(curr) in [3, 4, 5]:
                season = 2
            elif int(curr) in [6, 7, 8]:
                season = 3
            else:
                season = 4

            if season not in obs.season_to_loc:
                obs.season_to_loc[season] = []

            obs.season_to_loc[season].append((lats[x], long[x]))

        observations.append(obs)

    return observations


def observations_to_graph(observations: list[Observation]) -> Graph:
    """Builds 4 graphs from a list of Observation objects (one for each season), by
    calling the graph building method. See Graph.build_from_observations for more details.

    Preconditions:
        - each Observation in the list has a valid species name and season_to_loc mapping
        - the list of observations is not empty
    """
    summer = Graph()
    spring = Graph()
    fall = Graph()
    winter = Graph()
    summer.build_from_observations(observations, 3)
    spring.build_from_observations(observations, 2)
    fall.build_from_observations(observations, 4)
    winter.build_from_observations(observations, 1)
    return summer, spring, fall, winter


def run_simulation(data_file: str, species_a: str, species_b: str) -> dict[str, float]:
    """Runs the data pipeline and computes seasonal proximity between two species."""
    clean_data("data.csv")
    observations = data_handle("new_file.csv")
    summer, spring, fall, winter = observations_to_graph(observations)

# import python_ta
   # python_ta.check_all(config={
    #'extra-imports': ['pandas', 'networkx'],  # the names (strs) of imported modules
    #'allowed-io': [],     # the names (strs) of functions that call print/open/input
    #'max-line-length': 120
#})
