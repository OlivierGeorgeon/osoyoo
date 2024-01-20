OUTCOME_NO_FOCUS = '0'
OUTCOME_LOST_FOCUS = 'L'
OUTCOME_FOCUS_TOO_CLOSE = 'TC'  # Go backward
OUTCOME_FOCUS_FRONT = 'F'  # Swipe or Watch
OUTCOME_FOCUS_SIDE = 'S'  # Turn
OUTCOME_FOCUS_FAR = 'FA'  # Go forward
OUTCOME_FOCUS_TOO_FAR = 'TF'  # U-Turn
OUTCOME_FLOOR = '11'
OUTCOME_TOUCH = 'T'
OUTCOME_LIST = [OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_FAR, OUTCOME_FOCUS_TOO_CLOSE, OUTCOME_FOCUS_FRONT,
                OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_TOO_FAR, OUTCOME_FLOOR]


class Interaction:
    def __init__(self, action, outcome, valence):
        self.action = action
        self.outcome = outcome
        self.valence = valence

    def __str__(self):
        """ Print interaction in the form <action><outcome>(<valence>) """
        return str(self.action) + str(self.outcome) + "(" + str(self.valence) + ")"

    def __hash__(self):
        """ The hash is necessary to use interactions as keys in a dictionary """
        return self.action.__hash__() * 10 + self.outcome.__hash__()

    def __eq__(self, other):
        """ Interactions are equal if they have the same action and the same outcome """
        if isinstance(other, self.__class__):
            return (self.action == other.action) and (self.outcome == other.outcome)
        else:
            return False


# Testing Interaction
# py -m autocat.Decider.Interaction
if __name__ == '__main__':
    """ demonstrate the usage of Interaction.create_or_retrieve() """
    interaction00 = Interaction.create_or_retrieve(0, OUTCOME_NO_FOCUS)  # Create
    interaction01 = Interaction.create_or_retrieve(0, 1)  # Create
    interaction10 = Interaction.create_or_retrieve(1, OUTCOME_NO_FOCUS)  # Create
    interaction11 = Interaction.create_or_retrieve(1, 1)  # Create
    interaction00b = Interaction.create_or_retrieve(0, OUTCOME_NO_FOCUS)  # Retrieve
