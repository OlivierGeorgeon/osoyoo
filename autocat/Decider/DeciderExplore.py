########################################################################################
# This decider makes the robot explore the parts of the terrain that are not yet known
########################################################################################

import numpy as np
from playsound import playsound
from . Action import ACTION_ALIGN_ROBOT, ACTION_FORWARD
from . Interaction import Interaction, OUTCOME_DEFAULT
from ..Robot.Enaction import Enaction

EXPLORATION_STEP_INIT = 0
EXPLORATION_STEP_ROTATE = 1
EXPLORATION_STEP_TRANSLATE = 2


class DeciderExplore:
    def __init__(self, workspace):
        self.workspace = workspace
        self.anticipated_outcome = OUTCOME_DEFAULT

        self.exploration_step = EXPLORATION_STEP_INIT
        self.prompt_point = np.array([-2000, 1500, 0])

    def propose_intended_enaction(self, enacted_interaction):
        """Propose the next intended enaction from the previous enacted interaction.
        This is the main method of the agent"""
        # Compute a specific outcome suited for this agent
        outcome = self.outcome(enacted_interaction)
        # Compute the intended enaction
        return self.intended_enaction(outcome)

    def outcome(self, enacted_interaction):
        """ Convert the enacted interaction into an outcome adapted to the explore behavior """
        return OUTCOME_DEFAULT

    def intended_enaction(self, outcome):
        """Return the next intended interaction"""
        # Compute the next prompt point
        if self.exploration_step == EXPLORATION_STEP_INIT:
            # Go back and forth
            # self.workspace.memory.egocentric_memory.prompt_point = self.prompt_point.copy()

            # If long time no see terrain origin
            if self.workspace.clock - self.workspace.memory.phenomenon_memory.phenomena[0].last_origin_clock > 5:
                # If near the terrain origin then go to confirmation prompt
                if self.workspace.memory.is_near_terrain_origin():
                    allo_confirmation = self.workspace.memory.phenomenon_memory.phenomena[0].confirmation_prompt()
                    print("Enact confirmation affordance to allocentric", allo_confirmation)
                    ego_confirmation = self.workspace.memory.allocentric_to_egocentric(allo_confirmation)
                    self.workspace.memory.egocentric_memory.prompt_point = ego_confirmation
                    # TODO check how to ensure it does not keep doing that
                    playsound('autocat/Assets/R3.wav', False)
                else:
                    # If not near terrain origin then go to origin affordance point
                    allo_origin = self.workspace.memory.phenomenon_memory.phenomena[0].origin_affordance.experience.sensor_point.copy()
                    allo_origin += self.workspace.memory.phenomenon_memory.phenomena[0].point
                    print("Go to origin at allocentric:", allo_origin)
                    ego_origin = self.workspace.memory.allocentric_to_egocentric(allo_origin)
                    self.workspace.memory.egocentric_memory.prompt_point = ego_origin
                    playsound('autocat/Assets/R1.wav', False)
                    self.workspace.memory.phenomenon_memory.phenomena[0].last_origin_clock = self.workspace.clock
            else:
                # Go to the most interesting pool point
                # mip = self.workspace.memory.allocentric_memory.most_interesting_pool(self.workspace.clock)
                # self.workspace.memory.egocentric_memory.prompt_point = self.workspace.memory.allocentric_to_egocentric(mip)
                self.workspace.memory.egocentric_memory.prompt_point = self.prompt_point.copy()
            self.exploration_step = EXPLORATION_STEP_ROTATE

        # Compute the next intended interaction
        if self.exploration_step == EXPLORATION_STEP_TRANSLATE:
            action = self.workspace.actions[ACTION_FORWARD]
            self.exploration_step = EXPLORATION_STEP_INIT
        if self.exploration_step == EXPLORATION_STEP_ROTATE:
            action = self.workspace.actions[ACTION_ALIGN_ROBOT]
            self.exploration_step = EXPLORATION_STEP_TRANSLATE
        ii = Interaction.create_or_retrieve(action, self.anticipated_outcome)

        return Enaction(ii, self.workspace.clock, self.workspace.memory.egocentric_memory.focus_point,
                        self.workspace.memory.egocentric_memory.prompt_point)
