from pyrr import Matrix44, Quaternion
import math
import numpy as np
from .BodyView import BodyView
from autocat.Display.PointOfInterest import PointOfInterest, POINT_COMPASS, POINT_AZIMUTH
from ...Robot.CtrlRobot import ENACTION_STEP_REFRESHING
import circle_fit as cf
from ...Workspace import KEY_DECREASE, KEY_INCREASE
from ...Utils import quaternion_to_azimuth, quaternion_translation_to_matrix, translation_quaternion_to_matrix

KEY_OFFSET = 'O'


class CtrlBodyView:
    """Controls the body view"""
    def __init__(self, workspace):
        self.view = BodyView(workspace)
        self.workspace = workspace
        self.points_of_interest = []
        self.last_action = None
        self.mouse_press_x = 0
        self.mouse_press_y = 0
        self.mouse_press_angle = 0
        self.last_used_id = -1

        def on_text(text):
            """Process the user key or forward it to the Workspace to handle"""
            if text.upper() == KEY_DECREASE:
                self.workspace.memory.body_memory.energy = max(0, self.workspace.memory.body_memory.energy - 10)
                # self.workspace.memory_snapshot.body_memory.energy = self.workspace.memory.body_memory.energy
            elif text.upper() == KEY_INCREASE:
                self.workspace.memory.body_memory.energy = min(self.workspace.memory.body_memory.energy + 10, 100)
                # self.workspace.memory_snapshot.body_memory.energy = self.workspace.memory.body_memory.energy
            if text.upper() == KEY_OFFSET:
                # Calibrate the compass
                points = np.array([p.point()[0: 2] for p in self.points_of_interest if (p.type == POINT_AZIMUTH)])
                print(repr(points))
                if points.shape[0] > 2:
                    # Find the center of the circle made by the compass points
                    xc, yc, r, sigma = cf.taubinSVD(points)
                    # print("Fit circle", xc, yc, r, sigma)
                    if 130 < r < 550:  # 400
                        # If the radius is in bound then we can update de compass offset
                        delta_offset = np.array([xc, yc, 0], dtype=int)
                        self.workspace.memory.body_memory.compass_offset += delta_offset
                        position_matrix = Matrix44.from_translation(-delta_offset).astype('float64')
                        for p in self.points_of_interest:
                            p.displace(position_matrix)
                        self.view.label.text = "Compass offset adjusted by (" + str(round(xc)) + "," + str(round(yc)) + ")"
                    else:
                        self.view.label.text = "Compass calibration failed. Radius out of bound: " + str(round(r))
                else:
                    self.view.label.text = "Compass calibration failed. Insufficient points: " + str(points.shape[0])
            else:
                self.workspace.process_user_key(text)

        self.view.push_handlers(on_text)

    def add_point_of_interest(self, pose_matrix, point_type, group=None):
        """ Adding a point of interest to the view """
        if group is None:
            group = self.view.forefront
        point_of_interest = PointOfInterest(pose_matrix, self.view.batch, group, point_type, self.workspace.memory.clock)
        self.points_of_interest.append(point_of_interest)

    def update_body_view(self):
        """Add and update points of interest from the latest enacted interaction """

        # Update the position of the robot
        self.view.robot.rotate_head(self.workspace.memory.body_memory.head_direction_degree())
        self.view.robot.emotion_color(self.workspace.memory.emotion_code)
        # self.view.body_rotation_matrix = self.workspace.memory.body_memory.body_direction_matrix()

        # self.view.label.text = "Azimuth: " + str(azimuth) + "°"

        # Rotate the previous compass points so they remain at the south of the view
        # TODO rotate the compass points when imagining
        # if 'yaw' in self.workspace.enacted_interaction:
        # yaw = self.workspace.intended_enaction.yaw
        # displacement_matrix = matrix44.create_from_z_rotation(math.radians(yaw))
        for poi in [p for p in self.points_of_interest if p.type == POINT_COMPASS]:
            poi.displace(self.workspace.enaction.yaw_matrix)

        # Add the new points that indicate the south relative to the robot
        if self.workspace.enaction.outcome.compass_point is None:
            # No compass point then show the integrated south
            q = self.workspace.memory.body_memory.body_quaternion.inverse
            pose_matrix = translation_quaternion_to_matrix([0, -330, 0], q)
        else:
            # Show the compass south
            pose_matrix = quaternion_translation_to_matrix(self.workspace.enaction.compass_quaternion.inverse,
                                                           self.workspace.enaction.outcome.compass_point)
            self.add_point_of_interest(pose_matrix, POINT_COMPASS)
        self.add_point_of_interest(pose_matrix, POINT_AZIMUTH, self.view.background)

        # Fade the points of interest
        for poi in self.points_of_interest:
            poi.fade(self.workspace.memory.clock)
        # Keep only the points of interest during their durability
        for p in self.points_of_interest:
            if p.is_expired(self.workspace.memory.clock):
                p.delete()
        self.points_of_interest = [p for p in self.points_of_interest if not p.is_expired(self.workspace.memory.clock)]

    def main(self, dt):
        """Called every frame. Update the body view"""
        self.view.label_clock.text = "Clock: {:d}".format(self.workspace.memory.clock) \
                                     + ", En:{:d}%".format(self.workspace.memory.body_memory.energy) \
                                     + ", Ex:{:d}%".format(self.workspace.memory.body_memory.excitation) \
                                     + ", D:" + self.workspace.decider_id \
                                     + ", " + self.workspace.engagement_mode
        # During the interaction:update the head direction
        self.view.robot.rotate_head(self.workspace.memory.body_memory.head_direction_degree())
        # At the end of interaction
        if self.workspace.enacter.interaction_step == ENACTION_STEP_REFRESHING and self.workspace.enaction.outcome is not None:
            self.view.label.text = self.body_label_azimuth(self.workspace.enaction)
            self.view.label_enaction.text = self.body_label(self.workspace.enaction.action)
            self.update_body_view()

    def body_label(self, action):
        """Return the label to display in the body view"""
        rotation_speed = "{:.2f}°/s".format(math.degrees(action.rotation_speed_rad))
        label = "Speed x: " + str(int(action.translation_speed[0])) + "mm/s, y: " \
            + str(int(action.translation_speed[1])) + "mm/s, rotation:" + rotation_speed
        return label

    def body_label_azimuth(self, enaction):
        """Return the label to display in the body view"""
        azimuth = quaternion_to_azimuth(enaction.body_quaternion)
        if enaction.compass_quaternion is None:
            return "Azimuth: " + str(azimuth)
        else:
            compass = quaternion_to_azimuth(enaction.compass_quaternion)
            return "Azimuth: " + str(azimuth) + ", compass: " + str(compass) + ", delta: " + \
                   "{:.2f}".format(math.degrees(enaction.body_direction_delta))
