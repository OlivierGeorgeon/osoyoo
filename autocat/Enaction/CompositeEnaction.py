

class CompositeEnaction:
    def __init__(self, enactions):
        self.enactions = enactions
        self.index = 0

    def current_enaction(self):
        """Return the enaction at the current index"""
        assert self.index < len(self.enactions)
        return self.enactions[self.index]

    def increment(self):
        """Increment the current_index and return True if there is a next enaction"""
        self.index += 1
        if self.index < len(self.enactions):
            return True
        else:
            return False
