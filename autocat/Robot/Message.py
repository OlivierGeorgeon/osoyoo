import json
import math
from pyrr import Vector3, Quaternion
from .. Robot.RobotDefine import ROBOT_FRONT_X


class Message:
    """A message received from another robot"""
    def __init__(self, message_string):
        """Initialize the message object from the message_string"""

        print("Message", message_string)
        message_dict = json.loads(message_string)

        self.robot = message_dict['robot']
        self.body_quaternion = Quaternion.from_z_rotation(math.radians(90 - message_dict["azimuth"]))
        # if self.other_body_quaternion.angle > math.pi:
        #     self.other_body_quaternion *= -1

        self.destination = Vector3([0, 0, 0])
        if 'destination_x' in message_dict:
            self.destination = Vector3([message_dict["destination_x"], message_dict["destination_y"], 0])

        self.allo_position = None
        if 'pos_x' in message_dict:
            self.allo_position = Vector3([message_dict["pos_x"], message_dict["pos_y"], 0])
            self.allo_position += self.destination

        self.polar_ego_position = None
        if 'focus_x' in message_dict:
            # If focus then override the position
            self.focus_point = Vector3([message_dict["focus_x"], message_dict["focus_y"], 0])
            self.polar_ego_position = -self.focus_point * (1 + ROBOT_FRONT_X / self.focus_point.length)
            self.polar_ego_position += self.destination

        # Ego positions to be update by Workspace.receive_message
        self.ego_quaternion = None
        self.ego_position = None
