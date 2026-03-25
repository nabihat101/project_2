
import data_manipulation, entities
import os
import networkx as nx
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk

class Runner():
    """Class with methods for running the visualization
    
    Instance Attributes:
       - data_file: File where the original data is stored in a csv

    Representation Invariants:
       - data_file is a valid filepath that links to a csv file of the right format
    """
    data_file: str

    def __init__(self, data_file):
        self.data_file = data_file

    def _ask_species(self) -> entities.Graph:
        """ Ask the user which species and season, only returning when the
        values are valid inputs

        LEAVING THIS HERE FOR NOW BUT ITS NOT IN USE IM USING A DIFFERENT ONE
        """
        species_popup = entities.Popup(title = "Choose a species",
                             label = "Which species would you like to look at?")
        species = species_popup.text
        
        season_popup = entities.Popup(title = "Choose a season",
                                    label = "Which season would you like to look at? (summer, spring, fall, winter)")
        season = season_popup.text
        season = season.lower()

        while season not in {"spring", "summer", "fall", "winter"}:
            season_popup = entities.Popup(title = "Choose a season",
                                label = "Not a valid season name! (summer, spring, fall, winter)")
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
                        
        while not graph.is_vertex(species):
            
            species_popup = entities.Popup(title = "Choose a species",
                                     label = "That species doesn't have data for this season. Choose a species.")
            species_popup.display()
            species = species_popup.text
            season_popup = entities.Popup(title = "Choose a season",
                                    label = "Which season would you like to look at? (summer, spring, fall, winter)")
            season_popup.display()
            season = season_popup.text
            
            season = season.lower()

            while season not in {"spring", "summer", "fall", "winter"}:
                    season_popup = entities.Popup(title = "Choose a season",
                                            label = "Not a valid season name! (summer, spring, fall, winter)")
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
        species_graph.add_node(self._species)
        species = self._graph.get_vertex(self._species)
        for neighbour in self._graph.get_neighbours(self._species):
            species_graph.add_node(neighbour)
            species_graph.add_edge(self._species, neighbour, weight=species.get_weight(neighbour))
        return species_graph
    
    def display_window(self):
        """Display the window that lets you create a graph"""
        root = Tk()
        root.title('Species Interaction Visualizer')
        frm = ttk.Frame(root, padding=10)
        frm.grid()

        # Add text boxes for inputs
        ttk.Label(frm, text="Welcome to the species interaction visualizer!").grid(column=0, row=0)
        ttk.Label(frm, text="Input species").grid(column=1,row=1)
        self.species_input = entities.Textbox(frm, 0, 1)
        ttk.Label(frm, text="Input season").grid(column=1, row=2)
        self.season_input = entities.Textbox(frm, 0, 2)
        ttk.Label(frm, text="Proximity for co-occurence (m)").grid(column=1, row=3)
        self.prox_input = entities.Textbox(frm, 0, 3)

        # Buttons
        ttk.Button(frm, text="Quit", command=root.destroy).grid(column=2, row=0)
        ttk.Button(frm, text="Initialize Graph with current settings", command=self._initialize_graph_vals).grid(column=1,
                                                                                                                 row = 0)

        ttk.Label(frm, text="Graph statistics can go here").grid(column=0, row=4)
        root.mainloop()

    def _initialize_graph_vals(self):
        """Save the values in the textboxes, and draw and display the graph from them."""
        self.species_input.text = self.species_input.obj.get()
        self.season_input.text = self.season_input.obj.get()
        self.prox_input.text = self.prox_input.obj.get()

        if self.season_input.text == "spring":
            graph = self._spring
        elif self.season_input.text == "summer":
            graph = self._summer
        elif self.season_input.text == "fall":
            graph = self._fall
        elif self.season_input.text == "winter":
            graph = self._winter

        self._species = self.species_input.text
        self._graph = graph

        species_graph = self.create_species_graph()
        nx.draw_networkx(species_graph)
        plt.show()
    
    def run(self):
        """
        Run and create a graph based on user input
        """
        if "new_file.csv" not in os.listdir():
            data_manipulation.clean_data(self.data_file)
        self._observations = data_manipulation.data_handle("new_file.csv")
        self._summer, self._spring, self._fall, self._winter = data_manipulation.observations_to_graph(
            self._observations)
        
        self.display_window()

        
        

        
        
