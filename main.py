""" CSC111 Project 2

Module Description
==================
[INSERT DESCRIPTION]

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

def load_data(data_file: str) -> None:
    """
    Creates a datamap using pandas library to clean and filter data based on conditions

    Preconditions:
        - data_file refers to a csv containing species data and locations to be used in analysis
    """

    df = pd.read_csv(data_file)
    df_new = df.drop(columns=["id", "uuid", "observed_on_string", "time_observed_at", "time_zone", "user_id", "user_login", "user_name", "created_at", "updated_at", "quality_grade", "url", "image_url", "sound_url", "tag_list", "description", "num_identification_agreements", "num_identification_disagreements", "captive_cultivated", "oauth_application_id", "private_place_guess", "private_latitude", "private_longitude","public_positional_accuracy", "geoprivacy", "taxon_geoprivacy", "coordinates_obscured", "positioning_method", "positioning_device", "scientific_name", "iconic_taxon_name", "taxon_id", "common_name"])
    df_new = df_new[df_new["positional_accuracy"] <= 1000]
    print(df_new.head(40))

# import python_ta
   # python_ta.check_all(config={
    #'extra-imports': ['pandas', 'networkx'],  # the names (strs) of imported modules
    #'allowed-io': [],     # the names (strs) of functions that call print/open/input
    #'max-line-length': 120
#})
