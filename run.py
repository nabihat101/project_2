import math
import urllib.request
import urllib.error
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from PIL import Image
from io import BytesIO
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import data_manipulation
import entities
from utils import make_circular


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

    def create_species_graph(self):
        species_graph = nx.Graph()
        species = self._graph.get_vertex(self._species)
        species_graph.add_node(self._species, image=species.image, name=self._species)

        for neighbour in self._graph.get_neighbours(self._species):
            neighbour_v = self._graph.get_vertex(neighbour)
            species_graph.add_node(neighbour, image=neighbour_v.image, name=neighbour)

            x = species.get_prob(neighbour)

            # Safeguard to prevent log(0) crashes
            if x > 0:
                display_label = f"{x * 100:.2f}%"
                scaled_thickness = max(0.5, math.log10(x * 1000000))

                # Add the edge with the formatted label and scaled weight
                species_graph.add_edge(self._species, neighbour, weight=scaled_thickness, label=display_label)

        return species_graph

    def display_window(self):
        """Display the window that lets you create a graph"""

        root = tk.Tk()
        root.title('Species Interaction Visualizer')
        frm = ttk.Frame(root, padding=10)
        frm.grid()

        # Add text boxes for inputs
        ttk.Label(frm, text="Welcome to the species interaction visualizer!").grid(column=0, row=0)
        ttk.Label(frm, text="Input species").grid(column=1, row=1)
        self.species_input = entities.Textbox(frm, 0, 1)
        ttk.Label(frm, text="Input season").grid(column=1, row=2)
        self.season_input = entities.Textbox(frm, 0, 2)
        ttk.Label(frm, text="Proximity for co-occurence (m)").grid(column=1, row=3)
        self.prox_input = entities.Textbox(frm, 0, 3)

        # Buttons
        ttk.Button(frm, text="Quit", command=root.destroy).grid(column=2, row=0)
        ttk.Button(frm, text="Initialize Graph with current settings", command=self._initialize_graph_vals).grid(
            column=1,
            row=0)

        ttk.Label(frm, text="Graph statistics can go here").grid(column=0, row=4)
        # Add
        self.status_label = ttk.Label(frm, text="", foreground="red")
        self.status_label.grid(column=0, row=5)

        root.mainloop()

    def _initialize_graph_vals(self) -> None:
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
        else:
            self.status_label.config(text=f"Invalid season: {self.season_input.text}")
            return

        self._species = self.species_input.text
        self._graph = graph

        # CRASH PREVENTION: Check if the species exists in this season's graph before drawing!
        if not self._graph.is_vertex(self._species):
            self.status_label.config(text=f"Species '{self._species}' not found in {self.season_input.text}.")
            return

        self.status_label.config(text="")  # Clear errors

        species_graph = self.create_species_graph()
        # creates corrdinates for each node on graph
        pos = nx.spring_layout(species_graph, k=10)

        HOVER_TOOLTIPS = [
            ("name", "@name"),
        ]

        # creates the graph space: fig is the whole canvas and ax is the place where graph is drawn
        fig, ax = plt.subplots()

        # Draw each edge individually to bypass the NetworkX type stub error!
        # By passing a single float each time, the linter stays perfectly happy.
        for u, v in species_graph.edges():
            single_weight = float(species_graph.edges[u, v]['weight'])
            nx.draw_networkx_edges(species_graph, pos, edgelist=[(u, v)], width=single_weight, ax=ax)

        # get the labels for the edges so we can draw the percentages on
        edge_labels = nx.get_edge_attributes(species_graph, 'label')

        # draw labels using networkx at the position
        nx.draw_networkx_edge_labels(species_graph, pos, edge_labels=edge_labels, ax=ax)

        # draw images at node positions manually
        for n in species_graph.nodes():

            # get position of the node from before
            (x, y) = pos[n]

            # get the url from our nodes that we iniitalized previously
            img = species_graph.nodes[n]['image']
            # some of the images are in a Panda series format, not url. So we extract
            # the first part of this series which is the url
            if hasattr(img, "iloc"):
                img = img.iloc[0]

            # if the image is a string, since not all observations have images, we proceed to draw the image
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
            #plot = figure(tooltips=HOVER_TOOLTIPS, tools="pan,wheel_zoom,save,reset",
            #        active_scroll='wheel_zoom', title='my plot', sizing_mode='stretch_both', width=1000, height=1000)
            #plot.renderers.append(species_graph)

            # creates the actual image and shrinks it
            imagebox = OffsetImage(img, zoom=0.1)

            # puts image on the graph at the node position
            ab = AnnotationBbox(imagebox, (x, y), frameon=False)

            # draws image on the portion of canvas
            ax.add_artist(ab)

            # Remove axes for cleaner look
        ax.set_axis_off()

        # shows the graph
        plt.show()

        # https://networkx.org/documentation/stable/auto_examples/drawing/plot_custom_node_icons.html
        # https://stackoverflow.com/questions/44865023/how-can-i-create-a-circular-mask-for-a-numpy-array
        # https://matplotlib.org/stable/gallery/text_labels_and_annotations/demo_annotation_box.html
        # https://stackoverflow.com/questions/10678441/flipping-the-boolean-values-in-a-list-python

    def run(self):
        """Run and create a graph based on user input"""
        # Force the data cleaning to run every single time
        data_manipulation.clean_data(self.data_file)

        self._observations = data_manipulation.data_handle("new_file.csv")
        self._summer, self._spring, self._fall, self._winter = data_manipulation.observations_to_graph(
            self._observations)

        self.display_window()


if __name__ == '__main__':
    my_app = Runner("new_file.csv")
    my_app.run()
