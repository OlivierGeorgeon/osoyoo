# A place cell is defined by a point and contains the affordances experienced from this place
# A place cell can be recognized from its cues

class PlaceCell:

    def __init__(self, point, cues):
        """initialize the place cell from the point and a list of cues"""
        self.point = point.copy()
        self.key = round(self.point[0]), round(self.point[1])
        self.cues = cues

    def __hash__(self):
        return hash(self.key)

    def save(self):
        """Return a cloned place cell for memory snapshot"""
        return PlaceCell(self.point, {key: c.save() for key, c in self.cues.items()})
