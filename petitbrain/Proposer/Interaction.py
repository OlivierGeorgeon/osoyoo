OUTCOME_NO_FOCUS = 'no_focus'
OUTCOME_LOST_FOCUS = 'lost_focus'
OUTCOME_FOCUS_TOO_CLOSE = 'too_close'  # Go backward
OUTCOME_FOCUS_FRONT = 'front'  # Swipe or Watch
OUTCOME_FOCUS_SIDE = 'side'  # Turn
OUTCOME_FOCUS_FAR = 'far'  # Go forward
OUTCOME_FOCUS_TOO_FAR = 'too_far'  # U-Turn
OUTCOME_FLOOR = 'floor'
OUTCOME_TOUCH = 'touch'
OUTCOME_PROMPT = 'prompt'  # Reach the prompt point
OUTCOME_LIST = [OUTCOME_NO_FOCUS, OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_FAR, OUTCOME_FOCUS_TOO_CLOSE, OUTCOME_FOCUS_FRONT,
                OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_TOO_FAR, OUTCOME_FLOOR, OUTCOME_PROMPT]


class Interaction:
    def __init__(self, action, outcome, valence):
        self.action = action
        self.outcome = outcome
        self.key = (self.action.action_code, self.outcome)
        self.valence = valence

    def __str__(self):
        """ Print interaction in the form <action>_<outcome>:<valence> """
        return f"{self.action}_{self.outcome}:{self.valence}"
        # return self.key.__str__() + "<" + str(self.valence) + ">"

    def __hash__(self):
        """ The hash is necessary to use interactions as keys in a dictionary """
        return hash(self.key)

    def __eq__(self, other):
        """ Interactions are equal if they have the same action and the same outcome """
        if isinstance(other, Interaction):
            return self.key == other.key
        return NotImplemented
        # if isinstance(other, self.__class__):
        #     return (self.action == other.action) and (self.outcome == other.outcome)
        # else:
        #     return False


def create_interactions(actions):
    """Return the dictionary of all interactions with valence zero."""
    primitive_interactions = {}
    for a in actions.values():
        for o in OUTCOME_LIST:
            interaction = Interaction(a, o, 0)
            primitive_interactions[interaction.key] = interaction
    return primitive_interactions
