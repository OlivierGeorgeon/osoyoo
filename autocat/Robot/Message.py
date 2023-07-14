import json
import math
from pyrr import Vector3, Quaternion
from .. Robot.RobotDefine import ROBOT_FRONT_X


class Message:
    """A message recieved from another robot"""
    def __init__(self, message_string):
        print("Message", message_string)
        message_dict = json.loads(message_string)
        self.other_body_quaternion = Quaternion.from_z_rotation(math.radians(90 - message_dict["azimuth"]))
        # if self.other_body_quaternion.angle > math.pi:
        #     self.other_body_quaternion *= -1
        self.other_focus_point = Vector3([0, 0, 0])
        self.other_position = Vector3([0, 0, 0])
        self.other_destination = Vector3([0, 0, 0])
        if 'pos_x' in message_dict:
            self.other_position = Vector3([message_dict["pos_x"], message_dict["pos_y"], 0])
        if 'focus_x' in message_dict:
            # If focus then override the position
            self.other_focus_point = Vector3([message_dict["focus_x"], message_dict["focus_y"], 0])
            self.other_position = -self.other_focus_point * (1 + ROBOT_FRONT_X / self.other_focus_point.length)
        if 'destination_x' in message_dict:
            self.other_destination = self.other_position + Vector3(
                [message_dict["destination_x"], message_dict["destination_y"], 0])
        self.other_destination_ego = None  # Will be updated by CtrlRobot
