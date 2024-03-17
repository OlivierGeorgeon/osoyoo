import json
import math
from pyrr import Vector3, Quaternion
from .. Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X
from ..Memory.PhenomenonMemory import TERRAIN_INITIAL_CONFIDENCE
from ..Utils import azimuth_to_quaternion
from ..Utils import quaternion_translation_to_matrix


class Message:
    """A message received from another robot"""
    def __init__(self, message_string):
        """Initialize the message object from the message_string"""
        # Keep message_string for printing
        self.message_string = message_string

        message_dict = json.loads(message_string)

        self.robot = message_dict['robot']
        self.body_quaternion = azimuth_to_quaternion(message_dict["azimuth"])
        self.emotion_code = message_dict["emotion"]

        self.destination = Vector3([0, 0, 0])
        if 'destination' in message_dict:
            self.destination = Vector3(message_dict["destination"])

        self.ter_position = None
        if 'position' in message_dict:
            self.ter_position = Vector3(message_dict["position"])
            self.ter_position += self.destination

        self.polar_ego_position = None
        if 'focus' in message_dict:
            # If focus then compute the polar_ego position
            self.focus_point = Vector3(message_dict["focus"])
            self.polar_ego_position = -self.focus_point * (1 + ROBOT_FLOOR_SENSOR_X / self.focus_point.length)

        # Ego positions to be update by Workspace.receive_message
        self.position_matrix = None

    def set_position_matrix(self, memory):
        """Return the position matrix of the other robot in this egocentric memory"""
        # The relative position if available
        if self.ter_position is not None:
            # If position in terrain and this robot knows the position of the terrain
            if memory.phenomenon_memory.terrain_confidence() > TERRAIN_INITIAL_CONFIDENCE:
                ego_position = memory.terrain_centric_to_egocentric(self.ter_position)
            else:
                # If cannot place the robot then no position matrix
                return
        elif self.polar_ego_position is not None:
            # If only focus position was received then we assume this robot is in the other's focus
            ego_position = memory.polar_egocentric_to_egocentric(self.polar_ego_position)
        else:
            return
        # The relative direction of the other robot
        ego_quaternion = self.body_quaternion.cross(memory.body_memory.body_quaternion.inverse)
        # The position matrix
        self.position_matrix = quaternion_translation_to_matrix(ego_quaternion, ego_position)
