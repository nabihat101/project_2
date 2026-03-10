class Vertex:
    species: str
    neighbours_weight: dict[str, int]

    def __init__(self, species: str) -> None:
        self.species = species
        self.neighbours = {}  # neighbour_species -> weight

class Graph:
    _vertices: dict[str, Vertex]
    
    def __init__(self) -> None:
        self._vertices = {}  # species -> Vertex
    
    def add_vertex(self, species: str) -> None:
        if species not in self._vertices:
            self._vertices[species] = Vertex(species)
