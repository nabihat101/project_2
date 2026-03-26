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

import tkinter as tk
from typing import Optional

from utils import haversine_distance_km, get_interaction_parameters, calculate_interaction_likelihood
from tkinter import ttk


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
    season_to_loc: dict[int, list[tuple[str, float, float]]]
    image: str

    def __init__(self, species: str, image: str) -> None:
        self.species = species
        self.season_to_loc = {}
        self.image = image


def get_observation(observations: list[Observation], target: str) -> Observation | None:
    for obs in observations:
        if obs.species == target:
            return obs


class Vertex:
    """Represents a vertex in the graph, which corresponds to a species in this case.

    Instance Attributes:
         - species: the name of the species represented by this vertex
         - neighbours: a mapping from neighbouring species to the weight of the edge between them
         - image: a url for the images of the species
         - neighbours_probability: a mapping from neighbouring species to the probability of the two species interacting
         based on functions in utils.py
    Representation Invariants:
         - species is a non-empty string
         - neighbours only contains keys that are valid species names (non-empty strings)
         - weights in neighbours are positive integers
    """
    species: str
    neighbours: dict[str, float]
    image: str
    neighbours_probability: dict[str, float]

    def __init__(self, species: str, image: str) -> None:
        self.species = species
        self.neighbours = {}  # neighbour_species -> weight
        self.image = image
        self.neighbours_probability = {}

    # FOR DEBUGGING PURPOSES
    def __repr__(self) -> str:
        """Returns a string representation of the Vertex."""
        return f"Vertex(species={self.species}, neighbours={self.neighbours})"

    def calculate_weighted_degree(self) -> int:
        """Return the sum of the weights in self.neighbours"""
        return sum(self.neighbours[neighbour] for neighbour in self.neighbours)

    def get_weight(self, species2: str) -> int:
        """Return the edge weight between the two vertices"""
        return self.neighbours[species2]

    def get_prob(self, species2: str) -> float:
        """Return the probability of interaction between the two vertices"""
        return self.neighbours_probability[species2]


class Graph:
    _vertices: dict[str, Vertex]

    def __init__(self) -> None:
        self._vertices = {}  # species -> Vertex

    def add_vertex(self, species: str, image: str) -> None:
        """Adds a vertex to the graph. Neighbours are added separately through add_edge.

        Preconditions:
            - species is a non-empty string representing the name of the species
        """
        if species not in self._vertices:
            self._vertices[species] = Vertex(species, image)

    def add_edge(self, s1: str, s2: str, im1: str, im2: str) -> None:
        """Adds an edge between two species in the graph, incrementing
        the weight if the edge already exists.

        Preconditions:
            - s1 and s2 are non-empty strings representing valid species names
            - s1 and s2 are not the same species (no self-loops)
        """
        if s1 == s2:
            return

        self.add_vertex(s1, im1)
        self.add_vertex(s2, im2)

        v1 = self._vertices[s1]
        v2 = self._vertices[s2]

        # Adding weights to the edges, or adding the edge if it doesn't exist
        if s2 in v1.neighbours:
            v1.neighbours[s2] += 1
        else:
            v1.neighbours[s2] = 1

        if s1 in v2.neighbours:
            v2.neighbours[s1] += 1
        else:
            v2.neighbours[s1] = 1

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
        species_season_to_loc = {}

        for observation in observations:
            if season in observation.season_to_loc:
                if observation.species not in species_season_to_loc:  # TO HANDLE CASES WHERE A SAME SPECIES IS OBSERVED MORE THAN ONCE
                    species_season_to_loc[observation.species] = [
                        (observation.season_to_loc[season], observation.image)]
                else:  # Add all the locations for this species in this season
                    species_season_to_loc[observation.species].extend([(observation.season_to_loc[season],
                                                                        observation.image)])  # Add in all locations for this season for this species
                if not observation.image.dropna().empty:
                    self.add_vertex(observation.species, observation.image.dropna().iloc[0])

                # If the species has no images, we use a stock image to represent them
                # its this duck right now but we should definitely change it to smth else
                else:
                    self.add_vertex(observation.species, 'https://static.inaturalist.org/photos/604719843/large.jpg')

        species_seen_in_season = list(species_season_to_loc.keys())
        # Add an edge between each pair of species observed in the same season.
        for i in range(len(species_seen_in_season) - 1):
            source_species = species_seen_in_season[i]

            for j in range(i + 1, len(species_seen_in_season)):
                target_species = species_seen_in_season[j]

                # create a nested list of images and locations
                locs1 = [l[0] for l in species_season_to_loc[source_species]]
                im1 = [l[1] for l in species_season_to_loc[source_species]]
                locs2 = [l[0] for l in species_season_to_loc[target_species]]
                im2 = [l[1] for l in species_season_to_loc[target_species]]

                # flatten the nested lists
                l1 = [l for x in locs1 for l in x]
                i1 = [l for x in im1 for l in x]
                l2 = [l for x in locs2 for l in x]
                i2 = [l for x in im2 for l in x]

                if not l1 or not l2:
                    continue
                else:
                    for k in range(len(l1)):
                        for l in range(len(l2)):

                            # extract the latitude and longitude from the (x,y,z) tuple
                            loc1 = (l1[k][1], l1[k][2])
                            loc2 = (l2[l][1], l2[l][2])

                            if haversine_distance_km(loc1, loc2) <= 1:
                                # updating the probabilities and the self.neighbours_probability attribute

                                co_occurrences, obs_a_count, obs_b_count = get_interaction_parameters(l1, l2, 1.0)
                                prob = calculate_interaction_likelihood(co_occurrences, obs_a_count, obs_b_count)

                                # add edge
                                self.add_edge(source_species, target_species, i1[k], i2[l])

                                # update prob dict.
                                v1 = self._vertices[source_species]
                                v2 = self._vertices[target_species]

                                v1.neighbours_probability[target_species] = prob
                                v2.neighbours_probability[source_species] = prob

    def is_vertex(self, species) -> bool:
        return species in self._vertices

    def get_vertex(self, species) -> Vertex:
        return self._vertices[species]

    def get_neighbours(self, species) -> list:
        """Return a list of neighbours of the given vertex"""
        return list(self._vertices[species].neighbours.keys())


class Textbox():
    """Class for user input in the tkinter GUI

    Instance Attributes:
        - text: User inputted text, or None if the text has not been submitted yet
        - row: The row of the textbox
        - col: the column of the textbox
        - frame: the tkinter frame the textbox is in
        - obj: the ttk.Entry object of the textbox
    """
    text: Optional[str]
    row: int
    col: int
    frame: ttk.Frame
    obj: ttk.Entry

    def __init__(self, frame: ttk.Frame, col: int, row: int):
        self.row = row
        self.col = col
        self.frame = frame
        self.text = None

        self.obj = ttk.Entry(frame)
        self.obj.grid(column=col, row=row)


class Popup():
    """Class for creating popup windows, essentially a GUI version of the
    input() command
    Instance Attributes:
        - text: The text from the popup window, or None if the popup window is
          not yet submitted
        - label: The popup window label
        - title: The popup window title
    """

    text: Optional[str]
    label: str
    title: str

    def __init__(self, label, title):
        self.text = None
        self.label = label
        self.title = title
        self.display()

    def display(self):
        """
        Display the popup window.
        """

        self._popup = tk.Tk()
        self._popup.title(self.title)
        label = tk.Label(self._popup, text=self.label)
        label.pack(padx=20, pady=20)
        self._entry = tk.Entry(self._popup)
        self._entry.pack(pady=10)
        submit_button = tk.Button(self._popup, text="Enter", command=self._get_text)
        submit_button.pack()

        self._popup.mainloop()

    def _get_text(self):
        """
        Set self.text to the popup text, only meant to be called from display
        """

        self.text = self._entry.get()
        self._popup.destroy()

# import python_ta
# python_ta.check_all(config={
# 'extra-imports': ['pandas', 'networkx'],  # the names (strs) of imported modules
# 'allowed-io': [],     # the names (strs) of functions that call print/open/input
# 'max-line-length': 120
# })
