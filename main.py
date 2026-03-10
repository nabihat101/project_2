import pandas as pd

def load_data(data_file: str) -> None:
    """
    Creates a datamap using pandas library to clean and filter data based on conditions

    preconditions:
    - data_file refers to a csv containing species data and locations to be used in analysis
    """

    df = pd.read_csv(data_file)
    df_new = df.drop(columns=["id", "uuid", "observed_on_string", "time_observed_at", "time_zone", "user_id", "user_login", "user_name", "created_at", "updated_at", "quality_grade", "url", "image_url", "sound_url", "tag_list", "description", "num_identification_agreements", "num_identification_disagreements", "captive_cultivated", "oauth_application_id", "private_place_guess", "private_latitude", "private_longitude","public_positional_accuracy", "geoprivacy", "taxon_geoprivacy", "coordinates_obscured", "positioning_method", "positioning_device", "scientific_name", "iconic_taxon_name", "taxon_id", "common_name"])
    df_new = df_new[df_new["positional_accuracy"] <= 1000]
    print(df_new.head(40))
