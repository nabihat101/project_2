class Vertex:
    def __init__(self, species: str) -> None:
        self.species = species
        self.neighbours = {}  # neighbour_species -> weight

class Graph:
    def __init__(self) -> None:
        self._vertices = {}  # species -> Vertex
