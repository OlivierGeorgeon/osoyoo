import math
import numpy as np
from pyrr import matrix44
from ..Robot.RobotDefine import FORWARD_SPEED, LATERAL_SPEED, DEFAULT_YAW, TURN_DURATION, TRANSLATE_DURATION
from ..Utils import rotate_vector_z

ACTION_FORWARD = '8'
ACTION_BACKWARD = '2'
ACTION_LEFTWARD = '4'
ACTION_RIGHTWARD = '6'
ACTION_TURN_LEFT = '1'
ACTION_TURN_RIGHT = '3'
ACTION_SCAN = '-'
ACTION_ALIGN_ROBOT = '/'
ACTION_ALIGN_HEAD = '*'

SIMULATION_TIME_RATIO = 1  # 0.5   # The simulation speed is slower than the real speed because ...
SIMULATION_STEP_OFF = 0
SIMULATION_STEP_ON = 1  # More step will be used to take wifi transmission time into account


class Action:
    """A primitive action that the robot can perform"""

    def __init__(self, action_code, translation_speed, rotation_speed, target_duration):
        self.action_code = action_code
        self.translation_speed = translation_speed
        self.rotation_speed_rad = rotation_speed
        self.target_duration = target_duration

        self.simulation_duration = target_duration
        self.simulation_rotation_speed = rotation_speed

        self.simulation_step = 0
        self.simulation_time = 0.
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
        """Set the new translation speed to the average between the previous and the argument"""
        # Adjust longitudinal speed only
        if self.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
            self.translation_speed[0] = (self.translation_speed[0] + translation[0]) / 2
            print("adjusting x speed: correction:", round(translation[0]),
                  "new x speed:", round(self.translation_speed[0]))
        # Adjust lateral speed only
        if self.action_code in [ACTION_LEFTWARD, ACTION_RIGHTWARD]:
            self.translation_speed[1] = (self.translation_speed[1] + translation[1]) / 2
            print("adjusting y speed: correction:", round(translation[1]),
                  "new y speed:", round(self.translation_speed[1]))

    def simulate(self, memory, dt):
        """Simulate the action in memory. Return True during the simulation, and False when it ends"""
        # Check the target time
        self.simulation_time += dt
        if self.simulation_time > self.simulation_duration:
            self.simulation_time = 0.
            self.simulation_step = SIMULATION_STEP_OFF
            return False

        # Simulate the displacement in egocentric memory
        translation_matrix = matrix44.create_from_translation(-self.translation_speed * dt * SIMULATION_TIME_RATIO)
        rotation_matrix = matrix44.create_from_z_rotation(self.simulation_rotation_speed * dt)
        displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
        for experience in memory.egocentric_memory.experiences.values():
            experience.displace(displacement_matrix)
        # Displacement in body memory
        memory.body_memory.body_direction_rad += self.simulation_rotation_speed * dt
        # Update allocentric memory
        memory.allocentric_memory.robot_point += rotate_vector_z(self.translation_speed * dt * SIMULATION_TIME_RATIO,
                                                                 memory.body_memory.body_direction_rad)
        memory.allocentric_memory.place_robot(memory.body_memory, 0)  # TODO add the clock

        return True

    def start_simulation(self, intended_interaction):
        """Initialize the simulation of the intended interaction"""
        self.simulation_step = SIMULATION_STEP_ON
        # Compute the duration and the speed depending and the intended interaction
        self.simulation_duration = self.target_duration
        self.simulation_rotation_speed = self. rotation_speed_rad
        # if self.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
        if 'duration' in intended_interaction:
            self.simulation_duration = intended_interaction['duration'] / 1000
        # if intended_interaction['action'] == ACTION_ALIGN_ROBOT:
        if 'angle' in intended_interaction:
            self.simulation_duration = math.fabs(intended_interaction['angle']) * TURN_DURATION / DEFAULT_YAW
            if intended_interaction['angle'] < 0:
                self.simulation_rotation_speed = -self.rotation_speed_rad
        self.simulation_duration *= SIMULATION_TIME_RATIO
        self.simulation_rotation_speed *= SIMULATION_TIME_RATIO


def create_actions():
    """Create all actions"""
    action_dictionary = {}

    forward_speed = np.array([FORWARD_SPEED, 0, 0], dtype=float)
    action_dictionary[ACTION_FORWARD] = Action(ACTION_FORWARD, forward_speed, 0, TRANSLATE_DURATION)

    backward_speed = np.array([-FORWARD_SPEED, 0, 0], dtype=float)
    action_dictionary[ACTION_BACKWARD] = Action(ACTION_BACKWARD, backward_speed, 0, TRANSLATE_DURATION)

    leftward_speed = np.array([0, LATERAL_SPEED, 0], dtype=float)
    action_dictionary[ACTION_LEFTWARD] = Action(ACTION_LEFTWARD, leftward_speed, 0, TRANSLATE_DURATION)

    rightward_speed = np.array([0, -LATERAL_SPEED, 0], dtype=float)
    action_dictionary[ACTION_RIGHTWARD] = Action(ACTION_RIGHTWARD, rightward_speed, 0, TRANSLATE_DURATION)

    null_speed = np.array([0, 0, 0], dtype=float)
    rotation_speed = math.radians(DEFAULT_YAW) / TURN_DURATION
    action_dictionary[ACTION_TURN_LEFT] = Action(ACTION_TURN_LEFT, null_speed, rotation_speed, TURN_DURATION)

    action_dictionary[ACTION_TURN_RIGHT] = Action(ACTION_TURN_RIGHT, null_speed, -rotation_speed, TURN_DURATION)

    action_dictionary[ACTION_ALIGN_ROBOT] = Action(ACTION_ALIGN_ROBOT, null_speed, rotation_speed, 1)

    action_dictionary[ACTION_SCAN] = Action(ACTION_SCAN, null_speed, 0, 2)
    action_dictionary[ACTION_ALIGN_HEAD] = Action(ACTION_ALIGN_HEAD, null_speed, 0, 1)

    return action_dictionary


# Initializing actions with predefined speeds
# py -m autocat.Decider.Action
if __name__ == '__main__':
    create_actions()
