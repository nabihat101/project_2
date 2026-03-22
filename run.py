import data_manipulation
from entities import Vertex, Graph, Observation, Popup
import os
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg


class Runner:
    """Class with methods for running the visualization

    Instance Attributes:
       - data_file: File where the original data is stored in a csv

    Representation Invariants:
       - data_file is a valid filepath that links to a csv file of the right format
    """
    data_file: str

    def __init__(self, data_file):
        self.data_file = data_file

    def _ask_species(self) -> Graph:
        """ Ask the user which species and season, only returning when the
        values are valid inputs
        """
        species_popup = Popup(title="Choose a species",
                                       label="Which species would you like to look at?")
        species_popup.display()
        species = species_popup.text

        season_popup = (
            Popup(title="Choose a season",
                                      label="Which season would you like to look at? (summer, spring, fall, winter)"))
        season_popup.display()
        season = season_popup.text
        season = season.lower()

        while season not in {"spring", "summer", "fall", "winter"}:
            season_popup = Popup(title="Choose a season",
                                          label="Not a valid season name! (summer, spring, fall, winter)")
            season_popup.display()
            season = season_popup.text
            season = season.lower()

        if season == "summer":
            graph = self._summer
        elif season == "spring":
            graph = self._spring
        elif season == "fall":
            graph = self._fall
        elif season == "winter":
            graph = self._winter

        while not graph.is_vertex(species) and species != "baby":

            species_popup = Popup(title="Choose a species",
                                           label="That species doesn't have data for this season. Choose a species.")
            species_popup.display()
            species = species_popup.text
            season_popup = Popup(title="Choose a season",
                                          label="Which season would you like to look at? (summer, spring, fall, winter)")
            season_popup.display()
            season = season_popup.text

            season = season.lower()

            while season not in {"spring", "summer", "fall", "winter"}:
                season_popup = Popup(title="Choose a season",
                                              label="Not a valid season name! (summer, spring, fall, winter)")
                season_popup.display()
                season = season_popup.text
                season = season.lower()

            if season == "summer":
                graph = self._summer
            elif season == "spring":
                graph = self._spring
            elif season == "fall":
                graph = self._fall
            elif season == "winter":
                graph = self._winter
        self._species = species
        self._graph = graph

    def create_species_graph(self):
        species_graph = nx.Graph()

        main_vertex = self._graph.get_vertex(self._species)
        species_graph.add_node(main_vertex)

        species_graph.add_node(self._species)
        species = self._graph.get_vertex(self._species)
        for neighbour in self._graph.get_neighbours(self._species):
            neighbour_vertex = self._graph.get_vertex(neighbour)

            species_graph.add_edge(self._species, neighbour_vertex, weight=species.get_weight(neighbour)*2)
        return species_graph

    def run(self):
        """
        Run and create a graph based on user input
        """
        if "new_file.csv" not in os.listdir():
            data_manipulation.clean_data(self.data_file)
        self._observations = data_manipulation.data_handle("new_file.csv")
        self._summer, self._spring, self._fall, self._winter = data_manipulation.observations_to_graph(
            self._observations)
        print(self._summer)
        self._ask_species()
        species_graph = self.create_species_graph()
        pos = nx.spring_layout(species_graph)


        plt.show()



