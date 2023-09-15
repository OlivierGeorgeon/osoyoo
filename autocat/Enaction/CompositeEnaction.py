

class CompositeEnaction:
    def __init__(self, enactions):
        self.enactions = enactions
        self.index = 0

    def current_enaction(self):
        """Return the enaction at the current index"""
        assert self.index < len(self.enactions)
        return self.enactions[self.index]

    def increment(self, outcome):
        """Move on to the next interaction or return False if end"""
        # If the enaction failed then abort
        # if outcome.impact > 0:
        #     return False
        self.index += 1
        # If no more enactions then return False
        if self.index >= len(self.enactions):
            return False

        return True
