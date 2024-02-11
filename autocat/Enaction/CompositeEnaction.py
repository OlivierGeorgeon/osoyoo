

class CompositeEnaction:
    """A composite enaction is a series of promitive interactions"""
    def __init__(self, enactions):
        self.enactions = enactions
        self.index = 0

    def __hash__(self):
        """The hash is the action code """
        # TODO improve
        return self.enactions[0].__hash__()

    def __eq__(self, other):
        """Enactions are equal if they have the same hash"""
        return self.__hash__() == other.__hash__()

    def current_enaction(self):
        """Return the enaction at the current index"""
        assert self.index < len(self.enactions)
        return self.enactions[self.index]

    def increment(self):
        """Move on to the next interaction or return False if end"""
        # If the primitive enaction failed then abort
        if not self.enactions[self.index].succeed():
            return False
        self.index += 1
        # If no more enactions then return False
        if self.index >= len(self.enactions):
            return False
        return True
