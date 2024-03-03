########################################################################################
# This proposer makes the robot arrange an object to a specific place
# Activation 4: when the robot is angry
########################################################################################
import math
import numpy as np
from pyrr import vector, line
from pyrr.geometric_tests import point_closest_point_on_line
from . Action import ACTION_SWIPE, ACTION_TURN, ACTION_FORWARD, ACTION_BACKWARD, ACTION_SCAN, ACTION_WATCH
from ..Robot.Enaction import Enaction
from ..Robot.Command import DIRECTION_LEFT, DIRECTION_RIGHT
from ..Robot.RobotDefine import CHECK_OUTSIDE, ROBOT_FLOOR_SENSOR_X
from . Proposer import Proposer
from ..Utils import line_intersection
from ..Enaction.CompositeEnaction import CompositeEnaction
from ..Memory import EMOTION_ANGRY
from . Interaction import OUTCOME_FLOOR, OUTCOME_LOST_FOCUS, OUTCOME_TOUCH, OUTCOME_NO_FOCUS
from ..Memory.PhenomenonMemory.PhenomenonTerrain import TERRAIN_INITIAL_CONFIDENCE
from ..Memory.PhenomenonMemory import ARRANGE_OBJECT_RADIUS

ARRANGE_MIN_RADIUS = 100
ARRANGE_MAX_RADIUS = 400
ARRANGE_ALIGNED_Y_MAX_OBJECT = 20   # The max Y on the robot-object axis to trigger pushing
ARRANGE_ALIGNED_Y_MAX_OFFSET = 100  # The max Y on the robot-object-axis to consider aligned

# STEP_INIT = 0
# STEP_ALIGN = 1
# STEP_WITHDRAW = 2


class ProposerArrange(Proposer):
    # def __init__(self, workspace):
    #     super().__init__(workspace)
    #     self.too_far = FOCUS_TOO_FAR_DISTANCE
    #     self.step = STEP_INIT

    def activation_level(self):
        """The level of activation of this decider: 0: default, 4: object to push, 3: withdraw."""
        if self.is_to_arrange():
            return 4
        elif self.is_to_withdraw():
            return 3  # May compete with ProposerExplore to return directly to origin
        return 0

        # activation_level = 0
        # # Activation 4 when angry: the highest of all deciders
        # if self.workspace.memory.emotion_code == EMOTION_ANGRY:
        #     activation_level = 4
        # # Activation 3 during the withdraw step, same as DeciderExplore
        # if self.step in [STEP_ALIGN, STEP_WITHDRAW]:
        #     activation_level = 3
        # return activation_level

    def select_enaction(self, enaction):
        """The enactions to push a object to a target place"""
        # print("Step", self.step)

        ego_target = self.workspace.memory.terrain_centric_to_egocentric(
            self.workspace.memory.phenomenon_memory.arrange_point())

        e_memory = self.workspace.memory.save()
        e_memory.emotion_code = EMOTION_ANGRY

        # If robot too close to target point then withdraw
        if self.is_to_withdraw():
            # Slight Withdraw
            e_memory.egocentric_memory.prompt_point = None
            # enaction_memory.egocentric_memory.focus_point = np.array([100, 0, 0])  # Look ahead but cause prediction error
            composite_enaction = Enaction(self.workspace.actions[ACTION_BACKWARD], e_memory)
            # self.step = STEP_INIT

        # If LOST FOCUS or impact then scan again
        elif enaction.outcome_code in [OUTCOME_NO_FOCUS, OUTCOME_LOST_FOCUS, OUTCOME_FLOOR]:
            # or self.workspace.memory.egocentric_memory.focus_point is None) and self.step in [STEP_INIT, STEP_ALIGN]:
            # enaction_memory = self.workspace.memory.save()
            e_memory.egocentric_memory.prompt_point = None
            composite_enaction = Enaction(self.workspace.actions[ACTION_SCAN], e_memory, span=10)
            # self.step = STEP_INIT  # Avoids systematically recalling DeciderArrange

        # If OUTCOME_TOUCH then push to target point without caution
        elif enaction.outcome_code == OUTCOME_TOUCH:
            # enaction_memory = self.workspace.memory.save()
            e_memory.egocentric_memory.prompt_point = np.array([ego_target[0] - ROBOT_FLOOR_SENSOR_X -
                                                                       ARRANGE_OBJECT_RADIUS, 0, 0])
            e_memory.egocentric_memory.focus_point = ego_target  # Look at target
            composite_enaction = Enaction(self.workspace.actions[ACTION_FORWARD], e_memory, caution=0)
            # self.step = STEP_WITHDRAW

        # If there is an object to arrange
        elif self.is_to_arrange():
            # The point center of the object is the focus
            # direction, distance = point_to_echo_direction_distance(self.workspace.memory.egocentric_memory.focus_point)
            # object_center = echo_point(direction, distance + ARRANGE_OBJECT_RADIUS)  # Presuppose the object's radius
            object_center = self.workspace.memory.egocentric_memory.focus_point
            l1 = line.create_from_points(object_center, ego_target)
            ego_intersection = line_intersection(l1, line.create_from_points([0, 0, 0], [0, 1, 0]))
            ego_projection = point_closest_point_on_line(np.array([0, 0, 0]), l1)
            print("Ego projection:", ego_projection, "object center:", object_center, "target:", ego_target)

            # If OUTCOME_FLOOR just turn around
            if enaction.outcome_code == OUTCOME_FLOOR:
                # self.step = STEP_INIT
                # enaction_memory = self.workspace.memory.save()
                e_memory.egocentric_memory.prompt_point = np.array([-500, 0, 0])
                e_memory.egocentric_memory.focus_point = np.array([-500, 0, 0])  # Look ahead
                composite_enaction = Enaction(self.workspace.actions[ACTION_TURN], e_memory, span=10)

            # If object behind target just watch (minus the radius to prevent keeping pushing)
            elif object_center[0] > ego_target[0] - ARRANGE_OBJECT_RADIUS:  # - ARRANGE_MIN_RADIUS:
                print("Object behind target:", ego_target[0] - object_center[0])
                # enaction_memory = self.workspace.memory.save()
                e_memory.egocentric_memory.prompt_point = None
                e_memory.egocentric_memory.focus_point = object_center  # Look at object
                composite_enaction = Enaction(self.workspace.actions[ACTION_WATCH], e_memory)
                # self.step = STEP_INIT

            # If object to push
            else:
                # self.step = STEP_ALIGN  # May be changed to STEP_PUSH
                # If robot-object-target not aligned
                if abs(ego_projection[1]) > ARRANGE_ALIGNED_Y_MAX_OFFSET:
                    # Go to the point from where to push
                    if CHECK_OUTSIDE == 1 and self.workspace.memory.is_outside_terrain(ego_projection):
                        print("Projection point inaccessible")
                        # enaction_memory = self.workspace.memory.save()
                        e_memory.egocentric_memory.prompt_point = None
                        e_memory.egocentric_memory.focus_point = object_center  # Look at object
                        composite_enaction = Enaction(self.workspace.actions[ACTION_WATCH], e_memory)
                        # self.step = STEP_INIT
                    # If angle to projection point greater than 20° and projection far enough from object
                    elif math.fabs(math.atan2(ego_projection[0], math.fabs(ego_projection[1]))) > 0.349 \
                            and object_center[0] - ego_projection[0] > 0 \
                            and np.linalg.norm(object_center - ego_projection) > ROBOT_FLOOR_SENSOR_X + \
                            ARRANGE_OBJECT_RADIUS:
                        # If prompt projection behind object swipe to prompt_intersection
                        # e_memory = self.workspace.memory.save()
                        e_memory.egocentric_memory.prompt_point = ego_projection
                        e_memory.egocentric_memory.focus_point = object_center  # Look at object
                        print("Turn and swipe to prompt projection", ego_projection)
                        # Turn the left to the projection
                        if ego_projection[1] > 0:
                            # Turn the left to the prompt
                            e0 = Enaction(self.workspace.actions[ACTION_TURN], e_memory, direction=DIRECTION_LEFT)
                        else:
                            # Turn the right to the prompt
                            e0 = Enaction(self.workspace.actions[ACTION_TURN], e_memory, direction=DIRECTION_RIGHT)
                        # Swipe to the prompt
                        e1 = Enaction(self.workspace.actions[ACTION_SWIPE], e0.predicted_memory.save())
                        composite_enaction = CompositeEnaction([e0, e1])
                    # If angle lower than 20°
                    elif CHECK_OUTSIDE == 1 and self.workspace.memory.is_outside_terrain(ego_intersection):
                        print("Intersection point inaccessible")
                        # e_memory = self.workspace.memory.save()
                        e_memory.egocentric_memory.prompt_point = None
                        e_memory.egocentric_memory.focus_point = object_center  # Look at object
                        composite_enaction = Enaction(self.workspace.actions[ACTION_WATCH], e_memory)
                        # self.step = STEP_INIT
                    else:
                        vector.set_length(ego_intersection, min(vector.length(ego_intersection), 500))
                        print("Swipe to intersection", ego_intersection)
                        # e_memory = self.workspace.memory.save()
                        e_memory.egocentric_memory.prompt_point = ego_intersection
                        e_memory.egocentric_memory.focus_point = object_center  # Look at object
                        composite_enaction = Enaction(self.workspace.actions[ACTION_SWIPE], e_memory)

                # If robot-object-target are aligned and object in front of robot
                elif abs(object_center[1]) < ARRANGE_ALIGNED_Y_MAX_OBJECT:
                    # If robot_direction also aligned with target by less than 10°
                    # subtract the radius of the robot and of the object
                    push_vector = vector.set_length(ego_target, np.linalg.norm(ego_target) - ROBOT_FLOOR_SENSOR_X -
                                                    ARRANGE_OBJECT_RADIUS)
                    self.workspace.memory.egocentric_memory.prompt_point = push_vector  # ego_target
                    # Push toward target
                    # e_memory = self.workspace.memory.save()
                    e_memory.egocentric_memory.prompt_point = np.array([ego_target[0] - ROBOT_FLOOR_SENSOR_X -
                                                                        ARRANGE_OBJECT_RADIUS, 0, 0])
                    e_memory.egocentric_memory.focus_point = ego_target  # Look at target
                    composite_enaction = Enaction(self.workspace.actions[ACTION_FORWARD], e_memory, caution=1)
                    # self.step = STEP_ALIGN
                # If robot-object-target are aligned but object not in front of robot
                else:
                    # Turn to object center
                    # e_memory = self.workspace.memory.save()
                    e_memory.egocentric_memory.prompt_point = object_center
                    e_memory.egocentric_memory.focus_point = object_center  # Look at object
                    composite_enaction = Enaction(self.workspace.actions[ACTION_TURN], e_memory)

        # Other cases that should not happen: just scan
        else:
            # e_memory = self.workspace.memory.save()
            e_memory.egocentric_memory.prompt_point = None
            e_memory.egocentric_memory.focus_point = None
            composite_enaction = Enaction(self.workspace.actions[ACTION_SCAN], e_memory, span=10)

        return composite_enaction

    def is_to_arrange(self):
        """Return True if the focus is not None and and at a location to arrange"""

        # If focus is None then don't arrange
        if self.workspace.memory.egocentric_memory.focus_point is None:
            return False

        # If no confident terrain then don't arrange object
        if self.workspace.memory.phenomenon_memory.terrain_confidence() <= TERRAIN_INITIAL_CONFIDENCE:
            print("No confident terrain")
            return False

        # If focus too far from terrain center then don't arrange object
        terrain_point = self.workspace.memory.egocentric_to_terrain_centric(
            self.workspace.memory.egocentric_memory.focus_point)
        # print("Focus in terrain-centric coordinates", terrain_point)
        if np.linalg.norm(terrain_point) > ARRANGE_MAX_RADIUS:
            print("Focus too far from terrain center:", np.linalg.norm(terrain_point))
            return False

        # If object farther than target point then don't arrange object
        ego_target = self.workspace.memory.terrain_centric_to_egocentric(
            self.workspace.memory.phenomenon_memory.arrange_point())
        # print("Ego focus", self.egocentric_memory.focus_point)
        # if object is closer than target point (minus the radius to prevent keeping pushing)
        if self.workspace.memory.egocentric_memory.focus_point[0] > ego_target[0] - ARRANGE_OBJECT_RADIUS:
            print("Object farther than target point")
            return False

        # If other robot is angry then don't arrange object
        if self.workspace.memory.phenomenon_memory.other_robot_is_angry():
            print("Other robot is angry")
            return False

        # All other cases: arrange the object
        return True

    def is_to_withdraw(self):
        """Return True if the robot is too close to the target point"""
        return np.linalg.norm(self.workspace.memory.terrain_centric_to_egocentric(
            self.workspace.memory.phenomenon_memory.arrange_point())) < 300
