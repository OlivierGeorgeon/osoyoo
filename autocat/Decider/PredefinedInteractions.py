from . Interaction import Interaction, OUTCOME_DEFAULT
from . CompositeInteraction import CompositeInteraction
from . Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_SWIPE, ACTION_RIGHTWARD, ACTION_TURN,  ACTION_SCAN, \
    ACTION_WATCH

# Circle object outcome

OUTCOME_LOST_FOCUS = 'L'

OUTCOME_FOCUS_TOO_CLOSE = 'TC'  # Go backward

OUTCOME_FOCUS_FRONT = 'F'  # Swipe or Watch
OUTCOME_FOCUS_SIDE = 'S'  # Turn

OUTCOME_FOCUS_FAR = 'FA'  # Go forward

OUTCOME_FOCUS_TOO_FAR = 'TF'  # U-Turn

OUTCOME_LIST = [OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_FAR, OUTCOME_FOCUS_TOO_CLOSE, OUTCOME_FOCUS_FRONT,
                OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_TOO_FAR]

# OUTCOME_FLOOR_LEFT = '10'
OUTCOME_FLOOR = '11'
# OUTCOME_FLOOR_RIGHT = '01'


def create_interactions(actions):
    """Create the interactions needed by AgentCircle"""

    # Create all the primitive interactions
    for a in actions.values():
        for o in OUTCOME_LIST:
            Interaction.create_or_retrieve(a, o)

    # Predefined behaviors used by DeciderCircle

    # When lost focus then scan
    i_4 = Interaction.create_or_retrieve(actions[ACTION_SCAN], OUTCOME_FOCUS_FRONT, 1)
    i_l = Interaction.create_or_retrieve(actions[ACTION_SCAN], OUTCOME_LOST_FOCUS, 1)
    for interaction in Interaction.interaction_list:
        if interaction != i_l and interaction.outcome in [OUTCOME_LOST_FOCUS]:
            CompositeInteraction.create_or_retrieve(interaction, i_4)

    # When scan and lost focus then turn left
    i14 = Interaction.create_or_retrieve(actions[ACTION_TURN], OUTCOME_FOCUS_FRONT, 1)
    CompositeInteraction.create_or_retrieve(i_l, i14)

    # When focus FRONT then swipe or Watch
    i4 = Interaction.create_or_retrieve(actions[ACTION_SWIPE], OUTCOME_DEFAULT, 2)  # Swipe has higher valence
    iw = Interaction.create_or_retrieve(actions[ACTION_WATCH], OUTCOME_DEFAULT, 1)
    for interaction in Interaction.interaction_list:
        if interaction.outcome in [OUTCOME_FOCUS_FRONT, OUTCOME_FLOOR]:  #, OUTCOME_RIGHT]:
            CompositeInteraction.create_or_retrieve(interaction, i4)
            CompositeInteraction.create_or_retrieve(interaction, iw)

    # When outcome NEARBY then WATCH
    # for interaction in Interaction.interaction_list:
    #     if interaction.outcome in [OUTCOME_FOCUS_FRONT]:
    #         CompositeInteraction.create_or_retrieve(interaction, iw)

    # When FAR FRONT then forward or watch
    i8 = Interaction.create_or_retrieve(actions[ACTION_FORWARD], OUTCOME_DEFAULT, 2)
    for interaction in Interaction.interaction_list:
        if interaction.outcome in [OUTCOME_FOCUS_FAR, OUTCOME_FOCUS_TOO_FAR]:
            CompositeInteraction.create_or_retrieve(interaction, i8)
            CompositeInteraction.create_or_retrieve(interaction, iw)

    # When TOO CLOSE then backward
    i24 = Interaction.create_or_retrieve(actions[ACTION_BACKWARD], OUTCOME_FOCUS_FRONT, 1)
    for interaction in Interaction.interaction_list:
        if interaction.outcome == OUTCOME_FOCUS_TOO_CLOSE:
            CompositeInteraction.create_or_retrieve(interaction, i24)

    # When focus on the SIDE or TOO FAR then turn
    for interaction in Interaction.interaction_list:
        if interaction.outcome in [OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_TOO_FAR]:  # , OUTCOME_FAR_RIGHT]:
            CompositeInteraction.create_or_retrieve(interaction, i14)

    ##################################
    # Trespassing outcome

    # Valence of trespassing interactions
    i80 = Interaction.create_or_retrieve(actions[ACTION_FORWARD], OUTCOME_DEFAULT, 4)
    # i810 = Interaction.create_or_retrieve(actions[ACTION_FORWARD], OUTCOME_FLOOR_LEFT, -2)
    i811 = Interaction.create_or_retrieve(actions[ACTION_FORWARD], OUTCOME_FLOOR, -2)
    # i801 = Interaction.create_or_retrieve(actions[ACTION_FORWARD], OUTCOME_FLOOR_RIGHT, -2)

    i40 = Interaction.create_or_retrieve(actions[ACTION_SWIPE], OUTCOME_DEFAULT, 1)
    # i410 = Interaction.create_or_retrieve(actions[ACTION_SWIPE], OUTCOME_FLOOR_LEFT, -1)
    i411 = Interaction.create_or_retrieve(actions[ACTION_SWIPE], OUTCOME_FLOOR, 1)  # -1
    # i401 = Interaction.create_or_retrieve(actions[ACTION_SWIPE], OUTCOME_FLOOR_RIGHT, -1)

    i60 = Interaction.create_or_retrieve(actions[ACTION_RIGHTWARD], OUTCOME_DEFAULT, 1)
    # i610 = Interaction.create_or_retrieve(actions[ACTION_RIGHTWARD], OUTCOME_FLOOR_LEFT, -1)
    i611 = Interaction.create_or_retrieve(actions[ACTION_RIGHTWARD], OUTCOME_FLOOR, -1)
    # i601 = Interaction.create_or_retrieve(actions[ACTION_RIGHTWARD], OUTCOME_FLOOR_RIGHT, -1)

    i10 = Interaction.create_or_retrieve(actions[ACTION_TURN], OUTCOME_DEFAULT, -1)
    # i110 = Interaction.create_or_retrieve(actions[ACTION_TURN], OUTCOME_FLOOR_LEFT, -1)
    i111 = Interaction.create_or_retrieve(actions[ACTION_TURN], OUTCOME_FLOOR, -1)
    # i101 = Interaction.create_or_retrieve(actions[ACTION_TURN], OUTCOME_FLOOR_RIGHT, -1)

    # i30 = Interaction.create_or_retrieve(actions[ACTION_TURN_RIGHT], OUTCOME_DEFAULT, -2)
    # i310 = Interaction.create_or_retrieve(actions[ACTION_TURN_RIGHT], OUTCOME_FLOOR_LEFT, -2)
    # i311 = Interaction.create_or_retrieve(actions[ACTION_TURN_RIGHT], OUTCOME_FLOOR_FRONT, -2)
    # i301 = Interaction.create_or_retrieve(actions[ACTION_TURN_RIGHT], OUTCOME_FLOOR_RIGHT, -2)

    # When FLOOR then SWIPE left
    # for interaction in Interaction.interaction_list:
    #     if interaction.outcome in [OUTCOME_FLOOR_LEFT, OUTCOME_FLOOR_FRONT, OUTCOME_FLOOR_RIGHT]:
    #         CompositeInteraction.create_or_retrieve(interaction, i40)

    return CompositeInteraction.composite_interaction_list
