class Vertex:
    species: str
    neighbours: dict[str, int]

    def __init__(self, species: str) -> None:
        self.species = species
        self.neighbours = {}  # neighbour_species -> weight

    def __repr__(self) -> str:
        return f"Vertex(species={self.species}, neighbours={self.neighbours})"


class Graph:
    _vertices: dict[str, Vertex]

    def __init__(self) -> None:
        self._vertices = {}  # species -> Vertex

    def add_vertex(self, species: str) -> None:
        if species not in self._vertices:
            self._vertices[species] = Vertex(species)

    def add_edge(self, s1: str, s2: str) -> None:
        if s1 == s2:
            return
        self.add_vertex(s1)
        self.add_vertex(s2)

        v1 = self._vertices[s1]
        v2 = self._vertices[s2]

        # Adding weights to the edges
        if s2 in v1.neighbours:
            v1.neighbours[s2] += 1
        else:
            v1.neighbours[s2] = 1

        if s1 in v2.neighbours:
            v2.neighbours[s1] += 1
        else:
            v2.neighbours[s1] = 1

class Vertex: 
    species: str
    neighbours_weight: dict[str, int]

    def __init__(self, species: str) -> None:
        self.species = species
        self.neighbours = {}  # neighbour_species -> weight
    
    