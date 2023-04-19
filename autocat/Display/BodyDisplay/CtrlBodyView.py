from pyrr import matrix44
import math
from .BodyView import BodyView
from autocat.Display.PointOfInterest import PointOfInterest, POINT_COMPASS, POINT_AZIMUTH
from ...Workspace import INTERACTION_STEP_REFRESHING, INTERACTION_STEP_ENACTING
import numpy as np
import circle_fit as cf

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
            """Send user keypress to the workspace to handle"""
            if text.upper() == KEY_OFFSET:
                # Calibrate the compass
                points = np.array([[p.point[0], p.point[1]] for p in self.points_of_interest if (p.type == POINT_AZIMUTH)])
                print(repr(points))
                if points.shape[0] > 2:
                    # Find the center of the circle made by the compass points
                    xc, yc, r, sigma = cf.taubinSVD(points)
                    # print("Fit circle", xc, yc, r, sigma)
                    if 180 < r < 300:
                        # If the radius is in bound then we can update de compass offset
                        delta_offset = np.array([xc, yc, 0], dtype=int)
                        self.workspace.memory.body_memory.compass_offset += delta_offset
                        position_matrix = matrix44.create_from_translation(-delta_offset).astype('float64')
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

    def add_point_of_interest(self, x, y, point_type, group=None):
        """ Adding a point of interest to the view """
        if group is None:
            group = self.view.forefront
        point_of_interest = PointOfInterest(x, y, self.view.batch, group, point_type, self.workspace.clock)
        self.points_of_interest.append(point_of_interest)

    def update_body_view(self):
        """Add and update points of interest from the latest enacted interaction """

        # Update the position of the robot
        self.view.robot.rotate_head(self.workspace.memory.body_memory.head_direction_degree())
        azimuth = self.workspace.memory.body_memory.body_azimuth()
        self.view.body_rotation_matrix = self.workspace.memory.body_memory.body_direction_matrix()

        self.view.label.text = "Azimuth: " + str(azimuth) + "°"

        # Rotate the previous compass points so they remain at the south of the view
        # TODO rotate the compass points when imagining
        yaw = self.workspace.enacted_interaction['yaw']
        displacement_matrix = matrix44.create_from_z_rotation(math.radians(yaw))
        for poi in [p for p in self.points_of_interest if p.type == POINT_COMPASS]:
            poi.displace(displacement_matrix)

        # Add the new points that indicate the south relative to the robot
        if 'compass_x' in self.workspace.enacted_interaction:
            self.add_point_of_interest(self.workspace.enacted_interaction['compass_x'],
                                       self.workspace.enacted_interaction['compass_y'], POINT_COMPASS)
            self.add_point_of_interest(self.workspace.enacted_interaction['compass_x'],
                                       self.workspace.enacted_interaction['compass_y'], POINT_AZIMUTH,
                                       self.view.background)
            self.view.label.text += ", compass: " + str(self.workspace.enacted_interaction['azimuth']) + "°"
        else:
            # x = 300 * math.cos(math.radians(azimuth + 180))
            # y = 300 * math.sin(math.radians(azimuth + 180))
            # self.add_point_of_interest(x, y, POINT_COMPASS)
            x = 330 * math.cos(math.radians(azimuth + 180))
            y = 330 * math.sin(math.radians(azimuth + 180))
            self.add_point_of_interest(x, y, POINT_AZIMUTH, self.view.background)

        # Fade the points of interest
        for poi in self.points_of_interest:
            poi.fade(self.workspace.clock)
        # Keep only the points of interest during their durability
        for p in self.points_of_interest:
            if p.is_expired(self.workspace.clock):
                p.delete()
        self.points_of_interest = [p for p in self.points_of_interest if not p.is_expired(self.workspace.clock)]

    def main(self, dt):
        """Called every frame. Update the body view"""
        self.view.label_clock.text = "Clock: " + str(self.workspace.clock) \
                                     + ", Decider: " + self.workspace.decider_mode \
                                     + ", Engagement: " + self.workspace.engagement_mode
        if self.workspace.interaction_step == INTERACTION_STEP_ENACTING:
            self.view.label_enaction.text = self.workspace.intended_enaction.body_label()
        if self.workspace.interaction_step == INTERACTION_STEP_REFRESHING:
            self.update_body_view()
