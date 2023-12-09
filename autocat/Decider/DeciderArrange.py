########################################################################################
# This decider makes the robot arrange an object to a specific place
# Activation 4: when the robot is angry
########################################################################################
import math

from playsound import playsound
import numpy as np
from pyrr import vector, line
from pyrr.geometric_tests import point_closest_point_on_line
from . Action import ACTION_SWIPE, ACTION_TURN, ACTION_FORWARD, ACTION_BACKWARD, ACTION_SCAN, ACTION_WATCH
from ..Robot.Enaction import Enaction
from ..Robot.Command import DIRECTION_LEFT, DIRECTION_RIGHT
from ..Robot.RobotDefine import CHECK_OUTSIDE
from . Decider import Decider, FOCUS_TOO_FAR_DISTANCE
from ..Utils import line_intersection
from .. Enaction.CompositeEnaction import CompositeEnaction
from ..Memory.Memory import EMOTION_ANGRY, ARRANGE_MIN_RADIUS
from . Interaction import OUTCOME_FLOOR
from . Interaction import OUTCOME_LOST_FOCUS

STEP_INIT = 0
STEP_ALIGN = 1
STEP_WITHDRAW = 2


class DeciderArrange(Decider):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.too_far = FOCUS_TOO_FAR_DISTANCE
        self.action = self.workspace.actions[ACTION_SCAN]
        self.step = STEP_INIT

    def activation_level(self):
        """The level of activation of this decider: 0: default, 4 if angry, and then 3."""
        activation_level = 0
        # Activation 4 when angry: the highest of all deciders
        if self.workspace.memory.emotion_code == EMOTION_ANGRY:
            activation_level = 4
        # Activation 3 during the withdraw step, same as DeciderExplore
        if self.step in [STEP_ALIGN, STEP_WITHDRAW]:
            activation_level = 3
        return activation_level

    def select_enaction(self, outcome):
        """The enactions to push a object to a target place"""

        print("Step", self.step)
        # If LOST FOCUS or impact then scan again
        if outcome in [OUTCOME_LOST_FOCUS, OUTCOME_FLOOR] and self.step in [STEP_INIT, STEP_ALIGN]:
            composite_enaction = Enaction(self.workspace.actions[ACTION_SCAN], self.workspace.memory, span=10)
            self.step = STEP_INIT  # Avoids systematically recalling DeciderArrange
        # If STEP_INIT or previously aligned with focus
        elif self.step in [STEP_ALIGN, STEP_INIT]:
            ego_target = self.workspace.memory.terrain_centric_to_egocentric(
                self.workspace.memory.phenomenon_memory.arrange_point())
            l1 = line.create_from_points(self.workspace.memory.egocentric_memory.focus_point, ego_target)
            ego_prompt_intersection = line_intersection(l1, line.create_from_points([0, 0, 0], [0, 1, 0]))
            ego_prompt_projection = point_closest_point_on_line(np.array([0, 0, 0]), l1)
            print("Ego prompt projection:", ego_prompt_projection, "focus:",
                  self.workspace.memory.egocentric_memory.focus_point, "target:", ego_target)
            # If OUTCOME_FLOOR just scan
            if outcome == OUTCOME_FLOOR:
                self.step = STEP_INIT
                composite_enaction = Enaction(self.workspace.actions[ACTION_SCAN], self.workspace.memory, span=10)
            # If object behind target just watch
            elif ego_target[0] - self.workspace.memory.egocentric_memory.focus_point[0] < 0:
                print("Object behind target:", ego_target[0] - self.workspace.memory.egocentric_memory.focus_point[0])
                composite_enaction = Enaction(self.workspace.actions[ACTION_WATCH], self.workspace.memory)
                self.step = STEP_INIT
            # If object to push
            else:
                self.step = STEP_ALIGN  # May be changed to STEP_PUSH
                # If robot-object-target not aligned
                if math.fabs(ego_prompt_projection[1]) > 50:
                    # Go to the point from where to push
                    if CHECK_OUTSIDE == 1 and \
                       self.workspace.memory.is_outside_terrain(ego_prompt_projection):
                        print("Projection point inaccessible")
                        composite_enaction = Enaction(self.workspace.actions[ACTION_WATCH], self.workspace.memory)
                        self.step = STEP_INIT
                    # If angle to projection point greater than 20° and projection before object
                    elif math.fabs(math.atan2(ego_prompt_projection[0], math.fabs(ego_prompt_projection[1]))) > 0.349 \
                            and self.workspace.memory.egocentric_memory.focus_point[0] - ego_prompt_projection[0] > ARRANGE_MIN_RADIUS:
                        # If prompt projection behind object swipe to prompt_intersection
                        self.workspace.memory.egocentric_memory.prompt_point = ego_prompt_projection
                        # Turn the left to the projection
                        if ego_prompt_projection[1] > 0:
                            # Turn the left to the prompt
                            e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory,
                                          direction=DIRECTION_LEFT)
                        else:
                            # Turn the right to the prompt
                            e0 = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory,
                                          direction=DIRECTION_RIGHT)
                        # Swipe to the prompt
                        e1 = Enaction(self.workspace.actions[ACTION_SWIPE], e0.post_memory)
                        composite_enaction = CompositeEnaction([e0, e1])
                    # If angle lower than 20°
                    elif CHECK_OUTSIDE == 1 and self.workspace.memory.is_outside_terrain(ego_prompt_intersection):
                        print("Intersection point inaccessible")
                        composite_enaction = Enaction(self.workspace.actions[ACTION_WATCH], self.workspace.memory)
                        self.step = STEP_INIT
                    else:
                        print("Swipe to intersection", ego_prompt_intersection)
                        self.workspace.memory.egocentric_memory.prompt_point = ego_prompt_intersection
                        composite_enaction = Enaction(self.workspace.actions[ACTION_SWIPE], self.workspace.memory)
                # If robot_point-object-target are aligned
                else:
                    # If robot_direction also aligned with target by less than 10°
                    # subtract the radius of the robot and of the object
                    push_vector = vector.set_length(ego_target, np.linalg.norm(ego_target) - ARRANGE_MIN_RADIUS)
                    self.workspace.memory.egocentric_memory.prompt_point = push_vector  # ego_target
                    if math.fabs(math.atan2(ego_target[1], ego_target[0])) < 0.17:  # 0.349:
                        # Push to target
                        self.workspace.memory.egocentric_memory.focus_point = ego_target.copy()  # Look at destination
                        composite_enaction = Enaction(self.workspace.actions[ACTION_FORWARD], self.workspace.memory)
                        self.step = STEP_WITHDRAW
                    # If robot_direction not aligned
                    else:
                        # Turn to target
                        composite_enaction = Enaction(self.workspace.actions[ACTION_TURN], self.workspace.memory)
        # If STEP_WITHDRAW
        else:
            # Slight Withdraw
            self.workspace.memory.egocentric_memory.prompt_point = None
            composite_enaction = Enaction(self.workspace.actions[ACTION_BACKWARD], self.workspace.memory)
            self.step = STEP_INIT

        return composite_enaction
