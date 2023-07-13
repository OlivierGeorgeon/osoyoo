########################################################################################
# This decider makes the robot stay in place and look at objects in its surrounding
# Activation 4: default.
########################################################################################

import json
import math
from playsound import playsound
import numpy as np
from pyrr import Quaternion, Vector3
from . Action import ACTION_WATCH, ACTION_TURN, ACTION_SWIPE, ACTION_FORWARD
from ..Robot.Enaction import Enaction
from . Decider import Decider
from .. Robot.RobotDefine import ROBOT_FRONT_X
from . PredefinedInteractions import create_or_retrieve_primitive, OUTCOME_FOCUS_SIDE, OUTCOME_FOCUS_FRONT, OUTCOME_FOCUS_TOO_FAR


class DeciderWatch(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)

        # Give higher valence to Watch than to Swipe
        # TODO handle switching between deciders
        create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_SWIPE], OUTCOME_FOCUS_FRONT, 1)
        create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_FORWARD], OUTCOME_FOCUS_FRONT, 1)
        create_or_retrieve_primitive(self.primitive_interactions, workspace.actions[ACTION_WATCH], OUTCOME_FOCUS_FRONT, 2)

        self.action = self.workspace.actions[ACTION_WATCH]

    def activation_level(self):
        """The level of activation of this decider: 0: default, 2 if the terrain has an origin """
        return 4

    def outcome(self, enaction):
        """ Convert the enacted interaction into an outcome adapted to the watch behavior """

        outcome = super().outcome(enaction)

        # If a message was received
        if self.workspace.message is not None:
            print("Message", self.workspace.message)
            message_dict = json.loads(self.workspace.message)
            # other_body_quaternion = Quaternion.from_z_rotation(math.radians(90 - message_dict["azimuth"]))
            # if other_body_quaternion.angle > math.pi:
            #     other_body_quaternion = -other_body_quaternion
            focus_point = Vector3([message_dict["focus_x"], message_dict["focus_y"], 0])
            other_body_position = -focus_point * (1 + ROBOT_FRONT_X / focus_point.length)
            other_destination = other_body_position + Vector3([message_dict["destination_x"], message_dict["destination_y"], 0])

            other_destination_ego = self.workspace.memory.polar_egocentric_to_egocentric(other_destination)
            other_angle = math.atan2(other_destination_ego[1], other_destination_ego[0])
            other_direction_quaternion = Quaternion.from_z_rotation(other_angle)
            if math.fabs(other_angle) > math.pi / 6:
                # Focus on the other robot's destination
                print("Other polar destination point", other_destination)
                print("Other ego destination point", other_destination_ego)
                print("Other angle", math.degrees(other_angle))
                playsound('autocat/Assets/chirp.wav', False)
                self.workspace.memory.egocentric_memory.focus_point = other_destination_ego
                outcome = OUTCOME_FOCUS_SIDE
            self.workspace.message = None  # Delete the message

        return outcome

    def select_enaction(self, outcome):
        """Return the next intended interaction"""

        # Call the sequence learning mechanism to select the next action
        self.select_action(outcome)

        # Set the spatial modifiers
        if self.action.action_code in [ACTION_TURN]:
            if outcome == OUTCOME_FOCUS_TOO_FAR or self.workspace.memory.egocentric_memory.focus_point is None:
                # If focus TOO FAR or None then turn around
                self.workspace.memory.egocentric_memory.prompt_point = np.array([-100, 0, 0], dtype=int)
            else:
                # If focus SIDE then turn to the focus
                self.workspace.memory.egocentric_memory.prompt_point = \
                    self.workspace.memory.egocentric_memory.focus_point.copy()
        else:
            self.workspace.memory.egocentric_memory.prompt_point = None

        # Add the enaction to the stack
        self.workspace.enactions[self.workspace.clock] = Enaction(self.action, self.workspace.clock)
