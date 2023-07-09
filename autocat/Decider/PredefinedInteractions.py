from . Interaction import Interaction, OUTCOME_NO_FOCUS
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

OUTCOME_FLOOR = '11'


def create_interactions(actions):
    """Create the interactions needed by AgentCircle"""

    # Create all the primitive interactions with 0 valence
    for a in actions.values():
        for o in OUTCOME_LIST:
            Interaction.create_or_retrieve(a, o)

    # Predefined behaviors used by DeciderCircle

    # When lost focus then scan looking for focus front
    i_4 = Interaction.create_or_retrieve(actions[ACTION_SCAN], OUTCOME_FOCUS_FRONT, 1)
    i_0 = Interaction.create_or_retrieve(actions[ACTION_SCAN], OUTCOME_NO_FOCUS, 0)
    i_l = Interaction.create_or_retrieve(actions[ACTION_SCAN], OUTCOME_LOST_FOCUS, 0)
    for interaction in Interaction.interaction_list:
        if interaction.action.action_code != ACTION_SCAN and interaction.outcome in [OUTCOME_LOST_FOCUS]:
            CompositeInteraction.create_or_retrieve(interaction, i_4)

    # When scan and NO FOCUS or LOST or TOO FAR then turn looking for FOCUS FRONT
    i1f = Interaction.create_or_retrieve(actions[ACTION_TURN], OUTCOME_FOCUS_FRONT, 1)
    for interaction in Interaction.interaction_list:
        if interaction.action.action_code == ACTION_SCAN and interaction.outcome in [OUTCOME_LOST_FOCUS, OUTCOME_NO_FOCUS, OUTCOME_FOCUS_TOO_FAR]:
            CompositeInteraction.create_or_retrieve(interaction, i1f)

    # When focus FRONT or FLOOR then swipe or Watch looking for FOCUS FRONT OR SIDE
    i4f = Interaction.create_or_retrieve(actions[ACTION_SWIPE], OUTCOME_FOCUS_FRONT, 2)  # Swipe has higher valence
    iwf = Interaction.create_or_retrieve(actions[ACTION_WATCH], OUTCOME_FOCUS_FRONT, 1)
    for interaction in Interaction.interaction_list:
        if interaction.outcome in [OUTCOME_FOCUS_FRONT, OUTCOME_FLOOR]:
            CompositeInteraction.create_or_retrieve(interaction, i4f)
            CompositeInteraction.create_or_retrieve(interaction, iwf)

    # When FAR FRONT then forward or watch looking for FOCUS FRONT
    i8 = Interaction.create_or_retrieve(actions[ACTION_FORWARD], OUTCOME_FOCUS_FRONT, 2)
    for interaction in Interaction.interaction_list:
        if interaction.outcome in [OUTCOME_FOCUS_FAR]:  # OUTCOME_FOCUS_TOO_FAR]:
            CompositeInteraction.create_or_retrieve(interaction, i8)
            CompositeInteraction.create_or_retrieve(interaction, iwf)

    # When TOO CLOSE then backward looking for FOCUS FRONT
    i2f = Interaction.create_or_retrieve(actions[ACTION_BACKWARD], OUTCOME_FOCUS_FRONT, 1)
    for interaction in Interaction.interaction_list:
        if interaction.outcome == OUTCOME_FOCUS_TOO_CLOSE:
            CompositeInteraction.create_or_retrieve(interaction, i2f)

    # When focus on the SIDE or TOO FAR then turn looking for FOCUS FRONT
    for interaction in Interaction.interaction_list:
        if interaction.outcome in [OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_TOO_FAR]:  # , OUTCOME_FAR_RIGHT]:
            CompositeInteraction.create_or_retrieve(interaction, i1f)

    ##################################
    # Trespassing outcome

    # Valence of trespassing interactions
    i80 = Interaction.create_or_retrieve(actions[ACTION_FORWARD], OUTCOME_NO_FOCUS, 4)
    # i810 = Interaction.create_or_retrieve(actions[ACTION_FORWARD], OUTCOME_FLOOR_LEFT, -2)
    i811 = Interaction.create_or_retrieve(actions[ACTION_FORWARD], OUTCOME_FLOOR, -2)
    # i801 = Interaction.create_or_retrieve(actions[ACTION_FORWARD], OUTCOME_FLOOR_RIGHT, -2)

    i40 = Interaction.create_or_retrieve(actions[ACTION_SWIPE], OUTCOME_NO_FOCUS, 1)
    # i410 = Interaction.create_or_retrieve(actions[ACTION_SWIPE], OUTCOME_FLOOR_LEFT, -1)
    i411 = Interaction.create_or_retrieve(actions[ACTION_SWIPE], OUTCOME_FLOOR, 1)  # -1
    # i401 = Interaction.create_or_retrieve(actions[ACTION_SWIPE], OUTCOME_FLOOR_RIGHT, -1)

    i60 = Interaction.create_or_retrieve(actions[ACTION_RIGHTWARD], OUTCOME_NO_FOCUS, 1)
    # i610 = Interaction.create_or_retrieve(actions[ACTION_RIGHTWARD], OUTCOME_FLOOR_LEFT, -1)
    i611 = Interaction.create_or_retrieve(actions[ACTION_RIGHTWARD], OUTCOME_FLOOR, -1)
    # i601 = Interaction.create_or_retrieve(actions[ACTION_RIGHTWARD], OUTCOME_FLOOR_RIGHT, -1)

    i10 = Interaction.create_or_retrieve(actions[ACTION_TURN], OUTCOME_NO_FOCUS, -1)
    # i110 = Interaction.create_or_retrieve(actions[ACTION_TURN], OUTCOME_FLOOR_LEFT, -1)
    i111 = Interaction.create_or_retrieve(actions[ACTION_TURN], OUTCOME_FLOOR, -1)
    # i101 = Interaction.create_or_retrieve(actions[ACTION_TURN], OUTCOME_FLOOR_RIGHT, -1)

    return CompositeInteraction.composite_interaction_list
