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

from typing import Optional
from utils import get_interaction_parameters, calculate_interaction_likelihood
from utils import get_all_species
import tkinter as tk
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
    return None


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
        self.neighbours = {}  # neighbour_species -> likelihood float
        self.image = image
        self.neighbours_probability = {}

    def __repr__(self) -> str:
        """Returns a string representation of the Vertex."""
        return f"Vertex(species={self.species}, neighbours={self.neighbours})"

    def calculate_weighted_degree(self) -> int:
        """Return the sum of the weights in self.neighbours"""
        return sum(self.neighbours[neighbour] for neighbour in self.neighbours)

    def get_weight(self, species2: str) -> float:
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

    def add_edge(self, s1: str, s2: str, im1: str, im2: str, co_occurrences: int, prob: float) -> None:
        """Adds an edge between two species in the graph, storing both the raw
        co-occurrence count and the calculated interaction probability.

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

        # 1. Store the raw number of times they interacted
        v1.neighbours[s2] = co_occurrences
        v2.neighbours[s1] = co_occurrences

        # 2. Store the calculated statistical likelihood (0.0 to 1.0)
        v1.neighbours_probability[s2] = prob
        v2.neighbours_probability[s1] = prob

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
        species_data = {}  # species -> {'locs': list, 'image': str}

        # Gather all data and build vertices first
        for obs in observations:
            if season in obs.season_to_loc:

                # If we haven't seen this species yet, figure out its image and add the vertex
                if obs.species not in species_data:
                    # Fallback duck image
                    img_val = 'https://static.inaturalist.org/photos/604719843/large.jpg'

                    # Safely extract the image string (handling the pandas Series if it exists)
                    if hasattr(obs.image, 'dropna') and not obs.image.dropna().empty:
                        img_val = str(obs.image.dropna().iloc[0])
                    elif isinstance(obs.image, str) and obs.image.strip():
                        img_val = obs.image

                    species_data[obs.species] = {'locs': [], 'image': img_val}
                    self.add_vertex(obs.species, img_val)

                # Append all locations for this observation
                species_data[obs.species]['locs'].extend(obs.season_to_loc[season])

        species_seen = list(species_data.keys())

        # Compare each pair of species ONCE
        for i in range(len(species_seen) - 1):
            source_species = species_seen[i]

            for j in range(i + 1, len(species_seen)):
                target_species = species_seen[j]

                locs1 = species_data[source_species]['locs']
                locs2 = species_data[target_species]['locs']

                # Skip if one of them has no location data
                if not locs1 or not locs2:
                    continue

                co_occurrences, obs_a_count, obs_b_count = get_interaction_parameters(locs1, locs2, 1.0)

                # Only add the edge if they actually interacted
                if co_occurrences > 0:
                    prob = calculate_interaction_likelihood(co_occurrences, obs_a_count, obs_b_count)

                    im1 = species_data[source_species]['image']
                    im2 = species_data[target_species]['image']

                    self.add_edge(source_species, target_species, im1, im2, co_occurrences, prob)

                    # Update the exact probability float in neighbours_probability
                    v1 = self._vertices[source_species]
                    v2 = self._vertices[target_species]
                    v1.neighbours_probability[target_species] = prob
                    v2.neighbours_probability[source_species] = prob

    def is_vertex(self, species) -> bool:
        """
        Return if the species is a node and vertex in self._vertices
        """
        return species in self._vertices

    def get_vertex(self, species) -> Vertex:
        """
        Return the vertex object based on the species name

        Preconditions:
            - species in self._vertices
        """
        return self._vertices[species]

    def get_neighbours(self, species) -> list:
        """
        Return a list of neighbours of the given vertex

        Preconditions:
            - species in self._vertices
        """
        return list(self._vertices[species].neighbours.keys())

        
class SpeciesSearchDropdown():
    """New window for selecting a species from all the species.

    Instance Attributes:
        - window: The Tkinter window the button should be placed in.
        - species: The selected species, or None if one has not been selected yet.
        - all_species: A list of every species in the dataset.
    """
    window: tk.Tk
    species: Optional[str]
    all_species: list[str]
    
    def __init__(self, c: int, r: int, window: tk.Tk) -> None:
        self.window = window
        self.species = None

        # initialize the button to open the popup window
        open_button = ttk.Button(window, command = self.open_window,
                                 text = "Select a Species")
        open_button.grid(column = c, row = r, padx = 5, pady = 5, sticky="W")

        # initialize the text telling you the species
        self._species_label = ttk.Label(window,
                                       text = "Currently selected species: None")
        self._species_label.grid(column=c-1,row=r, padx=5, sticky="E")

    def open_window(self) -> None:
        """Open the species selector window"""
        self._new_win = tk.Toplevel(self.window)
        self._new_win.title("Select a Species")

        # center the new window
        x = self.window.winfo_screenwidth()
        y = self.window.winfo_screenheight()
        self._new_win.geometry(f"+{x//3}+{y//3}")
        
        # Text at the top of the window
        label = ttk.Label(self._new_win, text="Select a species from the list below")
        label.pack(side = tk.TOP)

        # Initialize the input area for users to type text
        self._input_area = ttk.Entry(self._new_win)
        self._input_area.pack()

        # make it so we run self.update_dropdown whenever any text
        # is inputted in the input area
        self._input_area.bind("<KeyRelease>", self.update_dropdown)

        # initialize the list of species, to be modified when we filter by the
        # text in the input area
        self.all_species = get_all_species('new_file.csv')
        self._species_list = tk.StringVar(value = self.all_species)
        
        # initialize the dropdown menu, showing all species initially
        self._dropdown = tk.Listbox(self._new_win,
                                   listvariable=self._species_list, selectmode="browse")
        self._dropdown.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)

        # bind it so we run enter_species when something in the list is clicked
        self._dropdown.bind("<<ListboxSelect>>", self.enter_species)

    def update_dropdown(self, event) -> None:
        """Update the listbox to show only species starting with the input in the
        entry box.
        """
        
        # get the text from the input area
        filter_text = self._input_area.get()

        # construct a new list of just species starting with that text
        new_species_list = [species for species in self.all_species
                            if filter_text.lower() in species.lower()]

        # update self.species_list to the new list
        self._species_list.set(new_species_list)

    def enter_species(self, event):
        """Set self.species to the selected species, and close the window."""

        # update self.species
        selected_index = self._dropdown.curselection()
        self.species = self._dropdown.get(selected_index)

        # update the text label
        self._species_label.config(text="Currently selected species: "+self.species)

        # close the window
        self._new_win.destroy()
        
if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
    'extra-imports': ['pandas', 'networkx', 'tkinter', 'math', 'matplotlib', 'urllib.request', 'numpy', 'Pillow', 'io', 'math', 'mplcursors'],  # the names (strs) of imported modules
    'allowed-io': [],     # the names (strs) of functions that call print/open/input
    'max-line-length': 120
    })

