from . Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_SWIPE, ACTION_RIGHTWARD, ACTION_TURN,  ACTION_SCAN, \
    ACTION_WATCH
from . Interaction import Interaction, OUTCOME_NO_FOCUS, OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_TOO_CLOSE, \
    OUTCOME_FOCUS_FAR, OUTCOME_FOCUS_SIDE,  OUTCOME_FOCUS_FRONT, OUTCOME_FLOOR, OUTCOME_FOCUS_TOO_FAR, OUTCOME_LIST
from . CompositeInteraction import CompositeInteraction

# # Circle object outcome
#
# OUTCOME_LOST_FOCUS = 'L'
#
# OUTCOME_FOCUS_TOO_CLOSE = 'TC'  # Go backward
#
# OUTCOME_FOCUS_FRONT = 'F'  # Swipe or Watch
# OUTCOME_FOCUS_SIDE = 'S'  # Turn
#
# OUTCOME_FOCUS_FAR = 'FA'  # Go forward
#
# OUTCOME_FOCUS_TOO_FAR = 'TF'  # U-Turn
#
# OUTCOME_LIST = [OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_FAR, OUTCOME_FOCUS_TOO_CLOSE, OUTCOME_FOCUS_FRONT,
#                 OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_TOO_FAR]
#
# OUTCOME_FLOOR = '11'


def create_or_retrieve_primitive(primitive_interactions, action, outcome, valence=None):
    """ Use this methode to create a new interaction or to retrieve it if it already exists """
    interaction = Interaction(action, outcome, valence if valence is not None else 0)

    if interaction in primitive_interactions:
        i = primitive_interactions.index(interaction)
        if valence is not None:
            primitive_interactions[i].valence = valence  # Update the valence
        # print("Retrieving ", cls.interaction_list[i])
        return primitive_interactions[i]
    else:
        # print("Creating ", interaction)
        primitive_interactions.append(interaction)
        return interaction


def create_or_reinforce_composite(composite_interactions, pre_interaction, post_interaction):
    interaction = CompositeInteraction(pre_interaction, post_interaction)

    if interaction in composite_interactions:
        i = composite_interactions.index(interaction)
        # print("reinforcing:", composite_interactions[i].__str__())
        composite_interactions[i].weight += 1
        return composite_interactions[i]
    else:
        # print("Learning:", interaction.__str__())
        composite_interactions.append(interaction)
        return interaction


def create_or_retrieve_composite(composite_interactions, pre_interaction, post_interaction):
    """Create ar retreive a composite interaction from the list """
    interaction = CompositeInteraction(pre_interaction, post_interaction)

    if interaction in composite_interactions:
        i = composite_interactions.index(interaction)
        # print("Retrieving ", end="")
        # print(cls.interaction_list[i])
        return composite_interactions[i]
    else:
        # print("Creating ", end="")
        # print(interaction)
        composite_interactions.append(interaction)
        return interaction


def create_primitive_interactions(actions):
    """Create all the primitive interactions with 0 valence"""
    primitive_interactions = []
    for a in actions.values():
        for o in OUTCOME_LIST:
            create_or_retrieve_primitive(primitive_interactions, a, o)
    return primitive_interactions


def create_composite_interactions(actions, primitive_interactions):
    """Create the interactions needed by AgentCircle"""

    composite_interactions = []

    # When lost focus then scan looking for focus front
    i_4 = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_SCAN], OUTCOME_FOCUS_FRONT, 1)
    i_0 = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_SCAN], OUTCOME_NO_FOCUS, 0)
    i_l = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_SCAN], OUTCOME_LOST_FOCUS, 0)
    for interaction in primitive_interactions:
        if interaction.action.action_code != ACTION_SCAN and interaction.outcome in [OUTCOME_LOST_FOCUS]:
            create_or_retrieve_composite(composite_interactions, interaction, i_4)

    # When scan and NO FOCUS or LOST or TOO FAR then turn looking for FOCUS FRONT
    i1f = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_TURN], OUTCOME_FOCUS_FRONT, 1)
    for interaction in primitive_interactions:
        if interaction.action.action_code == ACTION_SCAN and interaction.outcome in [OUTCOME_LOST_FOCUS, OUTCOME_NO_FOCUS, OUTCOME_FOCUS_TOO_FAR]:
            create_or_retrieve_composite(composite_interactions, interaction, i1f)

    # When focus FRONT or FLOOR then swipe or Watch looking for FOCUS FRONT OR SIDE
    i4f = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_SWIPE], OUTCOME_FOCUS_FRONT, 2)  # Swipe has higher valence
    iwf = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_WATCH], OUTCOME_FOCUS_FRONT, 1)
    for interaction in primitive_interactions:
        if interaction.outcome in [OUTCOME_FOCUS_FRONT, OUTCOME_FLOOR]:
            create_or_retrieve_composite(composite_interactions, interaction, i4f)
            create_or_retrieve_composite(composite_interactions, interaction, iwf)

    # When FAR FRONT then forward or watch looking for FOCUS FRONT
    i8 = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_FORWARD], OUTCOME_FOCUS_FRONT, 2)
    for interaction in primitive_interactions:
        if interaction.outcome in [OUTCOME_FOCUS_FAR]:  # OUTCOME_FOCUS_TOO_FAR]:
            create_or_retrieve_composite(composite_interactions, interaction, i8)
            create_or_retrieve_composite(composite_interactions, interaction, iwf)

    # When TOO CLOSE then backward looking for FOCUS FRONT
    i2f = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_BACKWARD], OUTCOME_FOCUS_FRONT, 1)
    for interaction in primitive_interactions:
        if interaction.outcome == OUTCOME_FOCUS_TOO_CLOSE:
            create_or_retrieve_composite(composite_interactions, interaction, i2f)

    # When focus on the SIDE or TOO FAR then turn looking for FOCUS FRONT
    for interaction in primitive_interactions:
        if interaction.outcome in [OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_TOO_FAR]:  # , OUTCOME_FAR_RIGHT]:
            create_or_retrieve_composite(composite_interactions, interaction, i1f)

    ##################################
    # Trespassing outcome

    # Valence of trespassing interactions
    i80 = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_FORWARD], OUTCOME_NO_FOCUS, 4)
    # i810 = Interaction.create_or_retrieve(actions[ACTION_FORWARD], OUTCOME_FLOOR_LEFT, -2)
    i811 = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_FORWARD], OUTCOME_FLOOR, -2)
    # i801 = Interaction.create_or_retrieve(actions[ACTION_FORWARD], OUTCOME_FLOOR_RIGHT, -2)

    i40 = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_SWIPE], OUTCOME_NO_FOCUS, 1)
    # i410 = Interaction.create_or_retrieve(actions[ACTION_SWIPE], OUTCOME_FLOOR_LEFT, -1)
    i411 = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_SWIPE], OUTCOME_FLOOR, 1)  # -1
    # i401 = Interaction.create_or_retrieve(actions[ACTION_SWIPE], OUTCOME_FLOOR_RIGHT, -1)

    i60 = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_RIGHTWARD], OUTCOME_NO_FOCUS, 1)
    # i610 = Interaction.create_or_retrieve(actions[ACTION_RIGHTWARD], OUTCOME_FLOOR_LEFT, -1)
    i611 = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_RIGHTWARD], OUTCOME_FLOOR, -1)
    # i601 = Interaction.create_or_retrieve(actions[ACTION_RIGHTWARD], OUTCOME_FLOOR_RIGHT, -1)

    i10 = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_TURN], OUTCOME_NO_FOCUS, -1)
    # i110 = Interaction.create_or_retrieve(actions[ACTION_TURN], OUTCOME_FLOOR_LEFT, -1)
    i111 = create_or_retrieve_primitive(primitive_interactions, actions[ACTION_TURN], OUTCOME_FLOOR, -1)
    # i101 = Interaction.create_or_retrieve(actions[ACTION_TURN], OUTCOME_FLOOR_RIGHT, -1)

    return composite_interactions
