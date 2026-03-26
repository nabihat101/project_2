""" CSC111 Project 2

Module Description
==================
This file contains all the classes used to represent the data and the graph structure for our analysis.
The main classes are:
- Observation: represents a species and the locations it was observed in different seasons
- Vertex: represents a vertex in the graph, which corresponds to a species in this case
- Graph: represents the graph structure

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 by Nabiha Tariq, Yusyra Hossain, Eleanor Neal, Ruoshui Deng
"""

from utils import haversine_distance_km, get_interaction_parameters, calculate_interaction_likelihood


class Observation:
    """
    Takes each observation and stores it in an object to make it easier to manipulate and build the graph.

    Instance Attributes:
        - species: the name of the species observed
        - season_to_loc: a mapping from season to a list of locations (latitude, longitude)
          where the species was observed in that season
    Representation Invariants:
        - season_to_loc only contains keys from 1 to 4, representing the four seasons
        - each location is a tuple of (latitude, longitude)
    """
    species: str
    # Updated: Now stores a list of (date_string, latitude, longitude)
    season_to_loc: dict[int, list[tuple[str, float, float]]]

    def __init__(self, species: str) -> None:
        self.species = species
        self.season_to_loc = {}


class Vertex:
    """Represents a vertex in the graph, which corresponds to a species in this case.

    Instance Attributes:
         - species: the name of the species represented by this vertex
         - neighbours: a mapping from neighbouring species to the weight of the edge between them
    Representation Invariants:
         - species is a non-empty string
         - neighbours only contains keys that are valid species names (non-empty strings)
         - weights in neighbours are positive integers
    """
    species: str
    # UPDATE: values are floats because likelihood is between 0.0 and 1.0
    neighbours: dict[str, float]

    def __init__(self, species: str) -> None:
        self.species = species
        self.neighbours = {}  # neighbour_species -> weight

    # FOR DEBUGGING PURPOSES
    def __repr__(self) -> str:
        """Returns a string representation of the Vertex."""
        return f"Vertex(species={self.species}, neighbours={self.neighbours})"


class Graph:
    _vertices: dict[str, Vertex]

    def __init__(self) -> None:
        self._vertices = {}  # species -> Vertex

    def add_vertex(self, species: str) -> None:
        """Adds a vertex to the graph. Neighbours are added separately through add_edge.

        Preconditions:
            - species is a non-empty string representing the name of the species
        """
        if species not in self._vertices:
            self._vertices[species] = Vertex(species)

    def add_edge(self, s1: str, s2: str, weight: float) -> None:
        """Adds an edge between two species in the graph, incrementing
        the weight if the edge already exists.

        Preconditions:
            - s1 and s2 are non-empty strings representing valid species names
            - s1 and s2 are not the same species (no self-loops)
        """
        if s1 == s2:
            return

        self.add_vertex(s1)
        self.add_vertex(s2)

        v1 = self._vertices[s1]
        v2 = self._vertices[s2]

        # Set the exact likelihood weight
        v1.neighbours[s2] = weight
        v2.neighbours[s1] = weight

    def build_from_observations(self, observations: list, season: int) -> None:
        """Builds a seasonal graph from observations.

        Each observation is a species with locations per season. For the given season,
        we add all species observed in that season as vertices, and create co-occurrence
        edges between species observed in the same season.

        Thus the graph represents co-occurrence of species in the same season,
        but does not show each individual observation.

        Preconditions:
            - season is between 1 and 4 inclusive.
            - observations is a list of objects with `species` and `season_to_loc`.
        """
        species_seen_in_season = []
        obs_dict = {}

        for observation in observations:
            if season in observation.season_to_loc:
                species_seen_in_season.append(observation.species)
                self.add_vertex(observation.species)
                obs_dict[observation.species] = observation

        for i in range(len(species_seen_in_season)):
            source_species = species_seen_in_season[i]
            for j in range(i + 1, len(species_seen_in_season)):
                target_species = species_seen_in_season[j]

                locs_a = obs_dict[source_species].season_to_loc[season]
                locs_b = obs_dict[target_species].season_to_loc[season]

                # Check for co-occurrences within 0.5 km on the exact same day
                co_occur, obs_a, obs_b = get_interaction_parameters(locs_a, locs_b, 1)

                # Only add edge if they actually co-occurred
                if co_occur > 0:
                    likelihood = calculate_interaction_likelihood(co_occur, obs_a, obs_b)
                    self.add_edge(source_species, target_species, likelihood)

    def __repr__(self) -> str:
        return f"Graph(vertices={list(self._vertices.keys())})"

# import python_ta
# python_ta.check_all(config={
# 'extra-imports': ['pandas', 'networkx'],  # the names (strs) of imported modules
# 'allowed-io': [],     # the names (strs) of functions that call print/open/input
# 'max-line-length': 120
# })
