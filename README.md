## Our Project

Our project uses real-world biodiversity observation data from [iNaturalist](https://www.inaturalist.org/), a platform where users can upload observations of animals they encounter. Each observation can include information such as the species name, observation date, geographic coordinates, images, and other metadata.

We originally planned to model biodiversity patterns across different animals, years, and locations. However, processing such a large dataset took too long, so we narrowed our dataset to **bird observations in Toronto from 2025**.

Even after filtering the dataset, there were still too many observations to create an interpretable model. We therefore capped the dataset at **6,000 observations**, randomly selected from the filtered bird observations.

### Data Cleaning

Before performing our analysis, we cleaned the dataset using **pandas** and kept only the variables needed for our project:

* `species_guess`: Name of the observed species
* `observed_on`: Date of the observation
* `latitude`: Latitude of the observation
* `longitude`: Longitude of the observation
* `image_url`: Reference image associated with the observation
* `positional_accuracy`: Integer representing the precision of the recorded location. A larger value indicates a less precise location.

We processed the original dataset with pandas by removing irrelevant columns and filtering observations based on our selected criteria.

The cleaned data is then converted into a list of `Observation` objects, which are instances of our `Observation` data class. This is the primary data structure we use for performing computations and generating our graph.

The `Observation` class stores the observed species and organizes its recorded locations by season, making the information easier to access and use throughout the program.

### Note

The dataset was limited to 6,000 randomly selected observations to keep processing time manageable and make the resulting analysis more interpretable.
