from pyrr import Matrix44, Quaternion
import math
import numpy as np
from .BodyView import BodyView
from autocat.Display.PointOfInterest import PointOfInterest
from ...Robot.CtrlRobot import ENACTION_STEP_RENDERING
from ...Workspace import KEY_DECREASE, KEY_INCREASE
from ...Utils import quaternion_to_azimuth
from ...Integrator.Calibrator import compass_calibration
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_COMPASS, EXPERIENCE_AZIMUTH

KEY_OFFSET = 'O'
ENGAGEMENT_MODES = {'R': "Real", 'I': "Imaginary"}


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
                points = np.array([p.point()[0: 2] for p in self.points_of_interest if (p.type == EXPERIENCE_AZIMUTH)])
                compass_xy = compass_calibration(points)
                if compass_xy is None:
                    self.view.label.text = "Compass calibration failed"
                else:
                    delta_offset = np.array([compass_xy[0], compass_xy[1], 0], dtype=int)
                    self.workspace.memory.body_memory.compass_offset += delta_offset
                    position_matrix = Matrix44.from_translation(-delta_offset).astype('float64')
                    for p in self.points_of_interest:
                        p.displace(position_matrix)
                    self.view.label.text = "Compass adjusted by " + str(compass_xy)
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

        # Delete the points of interest
        self.points_of_interest = [p for p in self.points_of_interest if not p.delete()]

        # Recreate the points of interest from experiences
        for e in [e for e in self.workspace.memory.egocentric_memory.experiences.values() if
                  e.clock + 10 >= self.workspace.memory.clock]:
            if e.type == EXPERIENCE_COMPASS:
                poi = PointOfInterest(e.pose_matrix, self.view.batch, self.view.forefront, e.type, e.clock,
                                      color_index=e.color_index)
                poi.fade(self.workspace.memory.clock)
                self.points_of_interest.append(poi)
            if e.type == EXPERIENCE_AZIMUTH:
                poi = PointOfInterest(e.pose_matrix, self.view.batch, self.view.background, e.type, e.clock,
                                      color_index=e.color_index)
                poi.fade(self.workspace.memory.clock)
                self.points_of_interest.append(poi)

    def main(self, dt):
        """Called every frame. Update the body view"""
        self.view.label_5HT.text = f"5-HT: {self.workspace.memory.body_memory.serotonin:d}"
        self.view.label_5HT.color = (0, 0, 0, 255) if self.workspace.memory.body_memory.serotonin >= 50 \
            else (255, 0, 0, 255)
        self.view.label_DA.text = f"DA: {self.workspace.memory.body_memory.dopamine:d}"
        if self.workspace.memory.body_memory.dopamine >= 50:
            self.view.label_DA.color = (0, 0, 0, 255)
        else:
            self.view.label_DA.color = (255, 0, 0, 255)
        self.view.label_NA.text = f"NA: {self.workspace.memory.body_memory.noradrenaline:d}"
        if self.workspace.memory.body_memory.noradrenaline >= 50:
            self.view.label_NA.color = (0, 0, 0, 255)
        else:
            self.view.label_NA.color = (255, 0, 0, 255)
        self.view.label_clock.text = "Clock: {:d}".format(self.workspace.memory.clock)  \
                                     + " | " + ENGAGEMENT_MODES[self.workspace.engagement_mode]  \
                                     + " | " + self.workspace.decider_id
        # + ", En:{:d}%".format(self.workspace.memory.body_memory.energy) \
        # + ", Ex:{:d}%".format(self.workspace.memory.body_memory.excitation) \

        # During the interaction:update the head direction
        self.view.robot.rotate_head(self.workspace.memory.body_memory.head_direction_degree())
        # At the end of interaction
        if self.workspace.enacter.interaction_step == ENACTION_STEP_RENDERING and self.workspace.enaction.outcome is not None:
            self.view.label.text = self.body_label_azimuth(self.workspace.enaction)
            self.view.label_enaction.text = self.body_label(self.workspace.enaction.action)
            self.update_body_view()

    def body_label(self, action):
        """Return the label to display in the body view"""
        # rotation_speed = "{:.1f}°/s".format(math.degrees(action.rotation_speed_rad))
        label = f"Translation: ({action.translation_speed[0]:.0f}, {action.translation_speed[1]:.0f}) mm/s, " \
                f"rotation: {math.degrees(action.rotation_speed_rad):.1f}°/s"
        return label

    def body_label_azimuth(self, enaction):
        """Return the label to display in the body view"""
        return "Azimuth: " + str(quaternion_to_azimuth(enaction.trajectory.body_quaternion)) + \
               ", offset: ({:d}, {:d})".format(self.workspace.memory.body_memory.compass_offset[0], self.workspace.memory.body_memory.compass_offset[1]) + \
               ", residual: {:.1f}".format(math.degrees(enaction.trajectory.body_direction_delta))
        # ", compass: " + str(quaternion_to_azimuth(enaction.trajectory.compass_quaternion)) + \
