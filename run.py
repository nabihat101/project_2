""" CSC111 Project 2

Module Description
==================
File that contains:
    - Runner class: Methods for running and creating interactive visualization such as:
        - Creating circular images 
        - Hovering over image to display information me
        - Popup handling 
        - User input
        - Creating the weighted graphs depending on season

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 by Nabiha Tariq, Yusyra Hossain, Eleanor Neal, Ruoshui Deng
"""

import data_manipulation, entities
from utils import make_circular
import os
import networkx as nx
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import urllib.request
import numpy as np
from PIL import Image
from io import BytesIO
from mplcursors import cursor
import math

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

    def create_species_graph(self):
        """
        Creates a networkx species graph using thresholds stated below to display only a portion of the entire graph using networkx.
        """
        
        species_graph = nx.Graph()
        species = self._graph.get_vertex(self._species)

        top_k = 4
        max_nodes = 50
        min_prob = 0.02  # 2% cutoff

        # a list of tuple (node_name, level of graph)
        queue = [(self._species, 0)]
        visited = set()

        # add first node
        species_graph.add_node(self._species, image=species.image, name=self._species, level=0)
        visited.add(self._species)

        while len(visited) < max_nodes:
            current, level = queue.pop()
            current_v = self._graph.get_vertex(current)

            neighbours = self._graph.get_neighbours(current)
            neighbours = sorted(neighbours, key=lambda n: current_v.get_prob(n), reverse=True)[:top_k]

            for neighbour in neighbours:
                x = current_v.get_prob(neighbour)

                if x < min_prob:
                    continue

                neighbour_v = self._graph.get_vertex(neighbour)

                if neighbour not in species_graph:
                    species_graph.add_node(neighbour, image=neighbour_v.image, name=neighbour, level=level+1)

                display_label = f"{x * 100:.2f}%"
                scaled_thickness = max(0.5, math.log10(x * 1000000))

                species_graph.add_edge(current, neighbour, weight=scaled_thickness, label=display_label)

                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append((neighbour, level+1))

        return species_graph

    def display_window(self):
        """
        Display the window that lets you create a graph using tkinter and adding the use input spaces and buttons.
        """
        
        root = Tk()
        root.title('Species Interaction Visualizer')
        frm = ttk.Frame(root)
        frm.grid(padx = 20, pady = 10)

        # Add text boxes and dropdown menus for inputs
        ttk.Label(frm, text="Welcome to the species interaction visualizer!", font=("TkDefaultFont", 14)).grid(column=0, row=0, pady=10, columnspan=2)
        self.species_input = entities.SpeciesSearchDropdown(c=1, r=1, window=frm)
        
        ttk.Label(frm, text="Input season: ").grid(column=0, row=2, padx=5, sticky="E")
        self.season_input = ttk.Combobox(frm, values = ['Spring', 'Summer', 'Fall', 'Winter'])
        self.season_input.grid(column=1, row=2, padx=5, pady = 5, sticky = "W")

        # Buttons
        ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=5, padx = 5, pady = 5)
        ttk.Button(frm, text="Initialize Graph with current settings", command=self._initialize_graph_vals).grid(
            column=0, row=5, padx = 5, pady = 5)

        self.status_label = ttk.Label(frm, text="", foreground="red")
        self.status_label.grid(column=0, row=4, columnspan=2)
        root.mainloop()

    def _initialize_graph_vals(self):
        """
        Save the values in the textboxes, and draw and display the graph from them.
        """
        
        self.season_input_text = self.season_input.get()

        if self.season_input_text == "Spring":
            graph = self._spring
        elif self.season_input_text == "Summer":
            graph = self._summer
        elif self.season_input_text == "Fall":
            graph = self._fall
        elif self.season_input_text == "Winter":
            graph = self._winter
        # Show an error if the user enters an invalid season input instead of selecting from the dropdown.
        else:
            self.status_label.config(text='Not a valid season.')
            return

        self._species = self.species_input.species
        self._graph = graph

        # CRASH PREVENTION: Check if the species exists in this season's graph before drawing!
        if not self._graph.is_vertex(self._species):
            self.status_label.config(text=f"Species '{self._species}' not found in {self.season_input_text}.")
            return

        self.status_label.config(text="")  # Clear errors

        species_graph = self.create_species_graph()
        # creates corrdinates for each node on graph
        pos = nx.spring_layout(species_graph, k=10)

        # creates the graph space: fig is the whole canvas and ax is the place where graph is drawn
        fig, ax = plt.subplots()

        # draw edges
        edges = species_graph.edges()
        weights = [species_graph[u][v]['weight'] for u, v in edges]
        weights = [w * 0.3 for w in weights]
        nx.draw_networkx_edges(species_graph, pos, ax=ax, width=weights)

        # node_info is a dict. storing a node name to it's neighbours and likelihood of interacting
        node_info = {}
        for node in species_graph.nodes():
            neighbours = []
            for nbr in species_graph.neighbors(node):

                # get the probability of a neighbour from label that we previously coded
                label = species_graph.edges[node, nbr].get("label", "")
                neighbours.append(f"{nbr}: {label}")

            # use join to create new lines by adding neighbours
            node_info[node] = "\n".join(neighbours)

        node_points = []

        # draw images at node positions manually
        for n in species_graph.nodes():

            # get position of the node from before and add to node_points with probabilities
            (x, y) = pos[n]
            node_points.append((x, y, n, node_info[n]))

            # get the url from our nodes that we iniitalized previously
            img = species_graph.nodes[n]['image']
            
            # some of the images are in a Panda series format, not url. So we extract
            # the first part of this series which is the url
            if hasattr(img, "iloc"):
                img = img.iloc[0]

            # if the image is a string, since not all observations have images, we proceed to draw the image
            if isinstance(img, str):

                # confirms the string is a URL
                if isinstance(img, str):

                    img_url = img  # Just to clarify the variable name
                    img = None  # Reset img so we can check if it loaded properly

                    # confirms the string is a URL
                    if img_url.startswith("http"):
                        try:
                            req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req) as response:
                                img_data = Image.open(BytesIO(response.read())).convert('RGBA')
                                img = np.array(img_data)
                        # Specifically catch network timeouts, 403 Forbidden, and corrupted image data
                        except (urllib.error.URLError, OSError) as e:
                            print(f"Failed to load image for {n}: {e}")
                    else:
                        try:
                            img = plt.imread(img_url)
                        # Specifically catch missing local files or unreadable image formats
                        except (FileNotFoundError, OSError):
                            pass

                    # Fallback if the image link is dead or forbidden: create a grey circle
                    if img is None:
                        img = np.full((100, 100, 4), [150, 150, 150, 255], dtype=np.uint8)

                img = make_circular(img)

            # creates the actual image and shrinks it
            imagebox = OffsetImage(img, zoom=0.1)

            # puts image on the graph at the node position
            ab = AnnotationBbox(imagebox, (x, y), frameon=False)

            # draws image on the portion of canvas
            ax.add_artist(ab)

        # Remove axes for cleaner look
        ax.set_axis_off()

        x_vals = [p[0] for p in node_points]
        y_vals = [p[1] for p in node_points]
        labels = [p[2] for p in node_points]

        # create cursor for the hover feature
        scatter = ax.scatter(x_vals, y_vals, s=100, alpha=0)
        crs = cursor(scatter, hover=True)

        # initialize text for the hover feature 
        crs.connect(
            "add",
            lambda sel: (
                sel.annotation.set_text(
                    f"{node_points[sel.index][2]}\nLikelihood of Interactions:\n{node_points[sel.index][3]}"
                ),
                sel.annotation.get_bbox_patch().set_alpha(1),
            )
        )

        # shows the graph
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




