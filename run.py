
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
        
    def create_species_graph(self) -> nx.Graph:
        """Initialize a networkx graph from our graph class"""
        
        species_graph = nx.Graph()

        # add a node for the target species
        species_graph.add_node(self._species)
        species = self._graph.get_vertex(self._species)

        # add nodes for each neighbour, and edges between the target species and neighbour
        for neighbour in self._graph.get_neighbours(self._species):
            species_graph.add_node(neighbour)
            species_graph.add_edge(self._species, neighbour, weight=species.get_weight(neighbour))
            
        return species_graph
    
    def display_window(self) -> None:
        """Display the window that lets you create a graph and specify parameters."""
        
        root = Tk()
        root.title('Species Interaction Visualizer')
        frm = ttk.Frame(root, padding=15)
        frm.pack()

        # Add text boxes for inputs
        ttk.Label(frm, text="Welcome to the species interaction visualizer!").grid(column=0, row=0, pady=5)
        ttk.Label(frm, text="Input species").grid(column=1,row=1,pady=5)
        self.species_input = entities.Textbox(frm, 0, 1)
        ttk.Label(frm, text="Input season").grid(column=1, row=2, pady=5)
        self.season_input = ttk.Combobox(frm, values = ["Spring", "Summer", "Fall", "Winter"])
        self.season_input.set("Select a season")
        self.season_input.grid(column=0, row=2, pady=5)
        ttk.Label(frm, text="Proximity for co-occurence (m)").grid(column=1, row=3, pady=5)
        self.prox_input = entities.Textbox(frm, 0, 3)

        # Buttons
        ttk.Button(frm, text="Quit", command=root.destroy).grid(column=2, row=0, padx=5, pady=5)
        ttk.Button(frm, text="Initialize Graph with current settings", command=self._initialize_graph_vals).grid(column=1,
                                                                                                                 row = 0, padx = 5, pady = 5)

        ttk.Label(frm, text="Graph statistics can go here").grid(column=0, row=4)
        root.mainloop()

    def _initialize_graph_vals(self) -> None:
        """Save the values in the textboxes, and draw and display the graph from them."""
        self.species_input.text = self.species_input.obj.get()
        self.season_input_text = self.season_input.get()
        self.prox_input.text = self.prox_input.obj.get()

        if self.season_input_text.lower() == "spring":
            graph = self._spring
        elif self.season_input_text.lower() == "summer":
            graph = self._summer
        elif self.season_input_text.lower() == "fall":
            graph = self._fall
        elif self.season_input_text.lower() == "winter":
            graph = self._winter

        self._species = self.species_input.text
        self._graph = graph

        species_graph = self.create_species_graph()
        nx.draw_networkx(species_graph)
        plt.show()
    
    def run(self) -> None:
        """
        Run and create a graph based on user input
        """
        if "new_file.csv" not in os.listdir():
            data_manipulation.clean_data(self.data_file)
        self._observations = data_manipulation.data_handle("new_file.csv")
        self._summer, self._spring, self._fall, self._winter = data_manipulation.observations_to_graph(
            self._observations)
        
        self.display_window()

        
        

        
        
