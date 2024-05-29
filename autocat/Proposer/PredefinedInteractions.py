from . Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_SWIPE, ACTION_RIGHTWARD, ACTION_TURN,  ACTION_SCAN, \
    ACTION_WATCH
from . Interaction import Interaction, OUTCOME_NO_FOCUS, OUTCOME_LOST_FOCUS, OUTCOME_FOCUS_TOO_CLOSE, \
    OUTCOME_FOCUS_FAR, OUTCOME_FOCUS_SIDE,  OUTCOME_FOCUS_FRONT, OUTCOME_FLOOR, OUTCOME_FOCUS_TOO_FAR, OUTCOME_LIST, OUTCOME_PROMPT
from . CompositeInteraction import CompositeInteraction


def create_or_retrieve_primitive(primitive_interactions, action, outcome, valence=None):
    """ Use this methode to create a new interaction or to retrieve it if it already exists """
    interaction = Interaction(action, outcome, valence if valence is not None else 0)

    if interaction in primitive_interactions:
        i = primitive_interactions.index(interaction)
        if valence is not None:
            primitive_interactions[i].valence = valence  # Update the valence
        # print("Retrieving ", primitive_interactions[i])
        return primitive_interactions[i]
    else:
        # print("Creating ", interaction)
        primitive_interactions.append(interaction)
        return interaction


def create_or_reinforce_composite(composite_interactions, pre_interaction, post_interaction):
    interaction = CompositeInteraction(pre_interaction, post_interaction)

    if interaction in composite_interactions:
        i = composite_interactions.index(interaction)
        # print("reinforcing:", composite_interactions[i])
        composite_interactions[i].weight += 1
        return composite_interactions[i]
    else:
        # print("Learning:", interaction)
        composite_interactions.append(interaction)
        return interaction


def create_or_retrieve_composite(composite_interactions, pre_interaction, post_interaction):
    """Create ar retreive a composite interaction from the list """
    interaction = CompositeInteraction(pre_interaction, post_interaction)

    if interaction in composite_interactions:
        i = composite_interactions.index(interaction)
        # print("Retrieving ", composite_interactions[i])
        return composite_interactions[i]
    else:
        # print("Creating ", interaction)
        composite_interactions.append(interaction)
        return interaction


# def create_primitive_interactions(actions):
#     """Create all the primitive interactions with 0 valence"""
#     primitive_interactions = []
#     for a in actions.values():
#         for o in OUTCOME_LIST:
#             create_or_retrieve_primitive(primitive_interactions, a, o)
#     return primitive_interactions


def create_composite_interactions(primitive_interactions):
    """Create the interactions needed by AgentCircle"""

    composite_interactions = []

    # When lost focus then scan looking for focus front
    i_4 = primitive_interactions[(ACTION_SCAN, OUTCOME_FOCUS_FRONT)]
    i_4.valence = 1
    for interaction in primitive_interactions.values():
        if interaction.action.action_code != ACTION_SCAN and interaction.outcome in [OUTCOME_LOST_FOCUS]:
            create_or_retrieve_composite(composite_interactions, interaction, i_4)

    # When scan and NO FOCUS or LOST or TOO FAR then turn looking for FOCUS FRONT
    i1f = primitive_interactions[(ACTION_TURN, OUTCOME_FOCUS_FRONT)]
    i1f.valence = 1
    for interaction in primitive_interactions.values():
        if interaction.action.action_code == ACTION_SCAN and interaction.outcome in [OUTCOME_LOST_FOCUS, OUTCOME_NO_FOCUS, OUTCOME_FOCUS_TOO_FAR]:
            create_or_retrieve_composite(composite_interactions, interaction, i1f)

    # When focus FRONT or FLOOR then swipe or Watch looking for FOCUS FRONT OR SIDE
    i4f = primitive_interactions[(ACTION_SWIPE, OUTCOME_FOCUS_FRONT)]  # Swipe has higher valence
    i4f.valence = 2
    iwf = primitive_interactions[(ACTION_WATCH, OUTCOME_FOCUS_FRONT)]
    for interaction in primitive_interactions.values():
        if interaction.outcome in [OUTCOME_FOCUS_FRONT, OUTCOME_FLOOR]:
            create_or_retrieve_composite(composite_interactions, interaction, i4f)
            create_or_retrieve_composite(composite_interactions, interaction, iwf)

    # When FAR FRONT then forward or watch looking for FOCUS FRONT
    i8 = primitive_interactions[(ACTION_FORWARD, OUTCOME_FOCUS_FRONT)]
    i8.valence = 2
    for interaction in primitive_interactions.values():
        if interaction.outcome in [OUTCOME_FOCUS_FAR]:  # OUTCOME_FOCUS_TOO_FAR]:
            create_or_retrieve_composite(composite_interactions, interaction, i8)
            create_or_retrieve_composite(composite_interactions, interaction, iwf)

    # When TOO CLOSE then backward looking for FOCUS FRONT
    i2f = primitive_interactions[(ACTION_BACKWARD, OUTCOME_FOCUS_FRONT)]
    i2f.valence = 1
    for interaction in primitive_interactions.values():
        if interaction.outcome == OUTCOME_FOCUS_TOO_CLOSE:
            create_or_retrieve_composite(composite_interactions, interaction, i2f)

    # When focus on the SIDE or TOO FAR then turn looking for FOCUS FRONT
    for interaction in primitive_interactions.values():
        if interaction.outcome in [OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_TOO_FAR]:  # , OUTCOME_FAR_RIGHT]:
            create_or_retrieve_composite(composite_interactions, interaction, i1f)

    ##################################
    # Trespassing outcome

    # Valence of trespassing interactions
    primitive_interactions[(ACTION_FORWARD, OUTCOME_NO_FOCUS)].valence = 4
    primitive_interactions[(ACTION_FORWARD, OUTCOME_FLOOR)].valence = 1  # Changed from -1 to 1 for IWAI paper

    primitive_interactions[(ACTION_SWIPE, OUTCOME_NO_FOCUS)].valence = 1
    primitive_interactions[(ACTION_SWIPE, OUTCOME_FLOOR)].valence = -1  # 1 -1

    primitive_interactions[(ACTION_RIGHTWARD, OUTCOME_NO_FOCUS)].valence = 1
    primitive_interactions[(ACTION_RIGHTWARD, OUTCOME_FLOOR)].valence= -1

    primitive_interactions[(ACTION_TURN, OUTCOME_NO_FOCUS)].valence = -1
    primitive_interactions[(ACTION_TURN, OUTCOME_FLOOR)].valence = -1

    return composite_interactions


def create_sequence_interactions(primitive_interactions):
    """Create the dictionary of predefined sequences of interaction"""
    sequence_interactions = {"TF-P": [primitive_interactions[(ACTION_TURN, OUTCOME_PROMPT)],
                                      primitive_interactions[(ACTION_FORWARD, OUTCOME_PROMPT)]],
                             "TF": [primitive_interactions[(ACTION_TURN, OUTCOME_FOCUS_FRONT)],
                                    primitive_interactions[(ACTION_FORWARD, OUTCOME_FLOOR)]],
                             "STF": [primitive_interactions[(ACTION_SWIPE, OUTCOME_PROMPT)],
                                     primitive_interactions[(ACTION_TURN, OUTCOME_FOCUS_FRONT)],
                                     primitive_interactions[(ACTION_FORWARD, OUTCOME_FLOOR)]]}
    return sequence_interactions
