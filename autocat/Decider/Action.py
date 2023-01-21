import math
import numpy as np
from ..Robot.RobotDefine import FORWARD_SPEED, LATERAL_SPEED, DEFAULT_YAW, TURN_DURATION
from ..Utils import rotate_vector_z

ACTION_FORWARD = '8'
ACTION_BACKWARD = '2'
ACTION_LEFTWARD = '4'
ACTION_RIGHTWARD = '6'
ACTION_TURN_LEFT = '1'
ACTION_TURN_RIGHT = '3'
ACTION_SCAN = '-'

SIMULATION_SPEED_RATIO = 1  # 0.5   # The simulation speed is slower than the real speed because ...
SIMULATION_TURN_RATIO = 1  # 0.75  # ... it covers the wifi communication time


class Action:
    """A primitive action that the robot can perform"""

    def __init__(self, action_code, translation_speed, rotation_speed, target_yaw, target_duration=1.):
        self.action_code = action_code
        self.translation_speed = translation_speed
        self.rotation_speed_rad = rotation_speed
        self.target_yaw = target_yaw
        self.target_duration = target_duration

        self.is_simulating = False
        self.simulation_target = 0.
        print("Create action", self, "of speed", self.translation_speed, "rotation speed", self.rotation_speed_rad)

    def __str__(self):
        """ Print the action as its action_code"""
        return self.action_code

    def __hash__(self):
        """ The hash is necessary to use actions as keys in a dictionary """
        return self.action_code.__hash__()

    def __eq__(self, other):
        """ Actions are equal if they have the same action_code """
        if isinstance(other, self.__class__):
            return self.action_code == other.action_code
        else:
            return False

    def adjust_translation_speed(self, translation):
        """Adjust the translation speed depending on the action"""
        if self.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
            self.translation_speed[0] = (self.translation_speed[0] + translation[0]) / 2
            print("adjusting x speed: correction:", round(translation[0]),
                  "new x speed:", round(self.translation_speed[0]))
        if self.action_code in [ACTION_LEFTWARD, ACTION_RIGHTWARD]:
            self.translation_speed[1] = (self.translation_speed[1] + translation[1]) / 2
            print("adjusting y speed: correction:", round(translation[1]),
                  "new y speed:", round(self.translation_speed[1]))

    def simulate(self, memory, dt):
        """Simulate the action in memory. Return True during the simulation, and False when it ends"""
        # Check the target
        if self.action_code in [ACTION_FORWARD, ACTION_BACKWARD, ACTION_RIGHTWARD, ACTION_LEFTWARD]:
            self.simulation_target += dt
            if self.simulation_target >= self.target_duration:
                self.simulation_target = 0
                self.is_simulating = False
                return False
        if self.action_code in [ACTION_TURN_LEFT, ACTION_TURN_RIGHT]:
            self.simulation_target += dt * math.fabs(self.rotation_speed_rad)
            if self.simulation_target >= math.radians(math.fabs(self.target_yaw)):
                self.simulation_target = 0
                self.is_simulating = False
                return False

        # simulate the action in memory
        memory.body_memory.body_direction_rad += self.rotation_speed_rad * dt * SIMULATION_TURN_RATIO
        memory.allocentric_memory.robot_point += rotate_vector_z(self.translation_speed * dt * SIMULATION_SPEED_RATIO,
                                                                 memory.body_memory.body_direction_rad)
        return True

    def start_simulation(self):
        if self.action_code in [ACTION_FORWARD, ACTION_BACKWARD, ACTION_RIGHTWARD, ACTION_LEFTWARD]:
            self.simulation_target = self.target_duration
        if self.action_code in [ACTION_TURN_RIGHT, ACTION_TURN_LEFT]:
            self.simulation_target = self.target_yaw


def create_actions():
    """Create all actions"""
    action_dictionary = {}

    forward_speed = np.array([FORWARD_SPEED, 0, 0], dtype=float)
    action_dictionary[ACTION_FORWARD] = Action(ACTION_FORWARD, forward_speed, 0, 0)

    backward_speed = np.array([-FORWARD_SPEED, 0, 0], dtype=float)
    action_dictionary[ACTION_BACKWARD] = Action(ACTION_BACKWARD, backward_speed, 0, 0)

    leftward_speed = np.array([0, LATERAL_SPEED, 0], dtype=float)
    action_dictionary[ACTION_LEFTWARD] = Action(ACTION_LEFTWARD, leftward_speed, 0, 0)

    rightward_speed = np.array([0, -LATERAL_SPEED, 0], dtype=float)
    action_dictionary[ACTION_RIGHTWARD] = Action(ACTION_RIGHTWARD, rightward_speed, 0, 0)

    null_speed = np.array([0, 0, 0], dtype=float)
    rotation_speed = math.radians(DEFAULT_YAW) / TURN_DURATION
    action_dictionary[ACTION_TURN_LEFT] = Action(ACTION_TURN_LEFT, null_speed, rotation_speed, DEFAULT_YAW)

    action_dictionary[ACTION_TURN_RIGHT] = Action(ACTION_TURN_RIGHT, null_speed, -rotation_speed, -DEFAULT_YAW)

    action_dictionary[ACTION_SCAN] = Action(ACTION_SCAN, null_speed, 0, 0)

    return action_dictionary


# Initializing actions with predefined speeds
# py -m autocat.Decider.Action
if __name__ == '__main__':
    create_actions()
