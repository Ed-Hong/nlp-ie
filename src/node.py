class Node(object):
    def __init__(self, name):
        self.name = name
        self.neighbors = [] # non-weighted edges
        self.weightedEdges = []

    def __repr__(self):
        return self.name

    def addWeightedEdge(self, neighbor, weight):
        self.weightedEdges.append(Edge(self.name, neighbor, weight))

class Edge(object):
    def __init__(self, source, dest, weight):
        self.source = source
        self.dest = dest
        self.weight = weight
        self.neighbors = []

    def __repr__(self):
        return self.source, self.dest, self.weight