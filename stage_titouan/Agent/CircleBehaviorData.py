from . Interaction import Interaction
from . CompositeInteraction import CompositeInteraction

ACTION_FORWARD = '8'
ACTION_BACKWARD = '2'
ACTION_LEFTWARD = '4'
ACTION_RIGHTWARD = '6'
ACTION_TURN_LEFT = '1'
ACTION_TURN_RIGHT = '3'
ACTION_SCAN = '-'

ACTION_LIST = [ACTION_FORWARD, ACTION_BACKWARD, ACTION_LEFTWARD, ACTION_RIGHTWARD, ACTION_TURN_LEFT, ACTION_TURN_RIGHT,
               ACTION_SCAN]

OUTCOME_LOST_FOCUS = 'L'
OUTCOME_FAR_FRONT = 'F'
OUTCOME_CLOSE_FRONT = 'C'
OUTCOME_LEFT = '4'
OUTCOME_RIGHT = '6'
OUTCOME_FAR_LEFT = '1'
OUTCOME_FAR_RIGHT = '3'

OUTCOME_LIST = [OUTCOME_LOST_FOCUS, OUTCOME_FAR_FRONT, OUTCOME_CLOSE_FRONT, OUTCOME_LEFT, OUTCOME_RIGHT,
                OUTCOME_FAR_LEFT, OUTCOME_FAR_RIGHT]

# Create all the primitive interactions
for a in ACTION_LIST:
    for o in OUTCOME_LIST:
        Interaction.create_or_retrieve(a, o)

# Predefine behaviors

# When lost focus then scan
i_4 = Interaction.create_or_retrieve(ACTION_SCAN, OUTCOME_LEFT)
i_l = Interaction.create_or_retrieve(ACTION_SCAN, OUTCOME_LOST_FOCUS)
for interaction in Interaction.interaction_list:
    if interaction != i_l:
        if interaction.outcome == OUTCOME_LOST_FOCUS:
            CompositeInteraction.create_or_retrieve(interaction, i_4)

# When scan and lost focus then turn left
i14 = Interaction.create_or_retrieve(ACTION_TURN_LEFT, OUTCOME_LEFT)
CompositeInteraction.create_or_retrieve(i_l, i14)

# Keep turning right
i44 = Interaction.create_or_retrieve(ACTION_LEFTWARD, OUTCOME_LEFT)
for interaction in Interaction.interaction_list:
    if interaction.outcome in [OUTCOME_LEFT, OUTCOME_RIGHT]:
        CompositeInteraction.create_or_retrieve(interaction, i44)

# When far front then forward
i84 = Interaction.create_or_retrieve(ACTION_FORWARD, OUTCOME_LEFT)
for interaction in Interaction.interaction_list:
    if interaction.outcome == OUTCOME_FAR_FRONT:
        CompositeInteraction.create_or_retrieve(interaction, i84)

# When close front then backward
i24 = Interaction.create_or_retrieve(ACTION_BACKWARD, OUTCOME_LEFT)
for interaction in Interaction.interaction_list:
    if interaction.outcome == OUTCOME_CLOSE_FRONT:
        CompositeInteraction.create_or_retrieve(interaction, i24)

# When far left then turn left
for interaction in Interaction.interaction_list:
    if interaction.outcome == OUTCOME_FAR_LEFT:
        CompositeInteraction.create_or_retrieve(interaction, i14)

# When far right then turn right
i34 = Interaction.create_or_retrieve(ACTION_TURN_RIGHT, OUTCOME_LEFT)
for interaction in Interaction.interaction_list:
    if interaction.outcome == OUTCOME_FAR_RIGHT:
        CompositeInteraction.create_or_retrieve(interaction, i34)
