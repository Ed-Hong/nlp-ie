class Node(object):
    def __init__(self, entity):
        self.entity = entity
        self.name = entity.text
        self.label = entity.label_
        self.neighbors = [] # non-weighted edges
        self.weightedEdges = []

    def __repr__(self):
        return self.name

    def addWeightedEdge(self, neighbor, relation, weight):
        self.weightedEdges.append(Edge(self, neighbor, relation, weight))

class Edge(object):
    def __init__(self, source, dest, relation, weight):
        self.src = source
        self.dst = dest
        self.relation = relation
        self.weight = weight