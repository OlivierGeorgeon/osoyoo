from pyrr import Matrix44
import math
import numpy as np
from .BodyView import BodyView
from autocat.Display.PointOfInterest import PointOfInterest
from ...Enaction import ENACTION_STEP_RENDERING
# from ...Workspace import KEY_DECREASE, KEY_INCREASE
from ...Utils import quaternion_to_azimuth
from ...Integrator.Calibrator import compass_calibration
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_COMPASS, EXPERIENCE_NORTH
from ...Memory.BodyMemory import DOPAMINE, SEROTONIN, NORADRENALINE

KEY_OFFSET = 'O'
ENGAGEMENT_MODES = {'R': "Real", 'I': "Imaginary"}


class CtrlBodyView:
    """Controls the body view"""
    def __init__(self, workspace):
        self.view = BodyView()
        self.view.set_caption("Robot " + workspace.robot_id)
        self.workspace = workspace
        self.points_of_interest = []
        self.last_action = None
        self.mouse_press_x = 0
        self.mouse_press_y = 0
        self.mouse_press_angle = 0
        self.last_used_id = -1

        def on_mouse_press(x, y, button, modifiers):
            """ Selecting or unselecting points of interest """
            self.view.mouse_to_ego_point(x, y, button, modifiers)

        def on_text(text):
            """Process the user key or forward it to the Workspace to handle"""
            # if text.upper() == KEY_DECREASE:
            #     self.workspace.memory.body_memory.energy = max(0, self.workspace.memory.body_memory.energy - 10)
            #     # self.workspace.memory_snapshot.body_memory.energy = self.workspace.memory.body_memory.energy
            # elif text.upper() == KEY_INCREASE:
            #     self.workspace.memory.body_memory.energy = min(self.workspace.memory.body_memory.energy + 10, 100)
            #     # self.workspace.memory_snapshot.body_memory.energy = self.workspace.memory.body_memory.energy
            if text.upper() == KEY_OFFSET:
                # Calibrate the compass
                points = np.array([p.point()[0: 2] for p in self.points_of_interest if (p.type == EXPERIENCE_NORTH)])
                compass_xy = compass_calibration(points)
                if compass_xy is None:
                    self.view.label2.text = "Compass calibration failed"
                else:
                    delta_offset = np.array([compass_xy[0], compass_xy[1], 0], dtype=int)
                    self.workspace.memory.body_memory.compass_offset += delta_offset
                    position_matrix = Matrix44.from_translation(-delta_offset).astype('float64')
                    for p in self.points_of_interest:
                        p.displace(position_matrix)
                    self.view.label2.text = "Compass adjusted by " + str(compass_xy)
            else:
                self.workspace.process_user_key(text)

        def on_mouse_scroll(x, y, dx, dy):
            """ Zooming the window or manually updating the neurotransmitter levels"""
            if y > 90:
                return
                # # Zoom the view
                # super().on_mouse_scroll(x, y, dx, dy)
            elif y > 60:
                # The neurotransmitter levels
                if x < 100:
                    self.workspace.memory.body_memory.neurotransmitters[DOPAMINE] += int(np.sign(dy))
                elif x < 190:
                    self.workspace.memory.body_memory.neurotransmitters[SEROTONIN] += int(np.sign(dy))
                else:
                    self.workspace.memory.body_memory.neurotransmitters[NORADRENALINE] += int(np.sign(dy))
            else:
                # The energy levels
                if x < 150:
                    self.workspace.memory.body_memory.energy += int(np.sign(dy))
                else:
                    self.workspace.memory.body_memory.excitation += int(np.sign(dy))

        self.view.push_handlers(on_mouse_press, on_text, on_mouse_scroll)

    def update_body_view(self):
        """Add and update points of interest from the latest enacted interaction """
        # Delete the expired points of interest
        self.points_of_interest = [p for p in self.points_of_interest if not p.delete(self.workspace.enaction.clock)]

        # Fade the remaining points of interest
        for p in self.points_of_interest:
            p.fade(self.workspace.memory.clock)

        # Create the new points of interest from the new experiences
        for e in [e for e in self.workspace.memory.egocentric_memory.experiences.values() if
                  e.clock == self.workspace.enaction.clock and e.type in [EXPERIENCE_COMPASS, EXPERIENCE_NORTH]]:
            # COMPASS Big blue diamonds are shown in the robot frame
            if e.type == EXPERIENCE_COMPASS:
                poi = PointOfInterest(e.pose_matrix, self.view.robot_batch, self.view.background, e.type, e.clock,
                                      e.color_index, 10)
            # NORTH Small blue diamonds are shown in polar frame
            else:
                poi = PointOfInterest(e.polar_pose_matrix(), self.view.polar_batch, self.view.forefront, e.type,
                                      e.clock, e.color_index, 10)
            self.points_of_interest.append(poi)

    def update_labels(self):
        """update the labels in body view"""
        label3 = f"Translation: ({self.workspace.enaction.action.translation_speed[0]:.0f}, " \
                 f"{self.workspace.enaction.action.translation_speed[1]:.0f}) mm/s, " \
                 f"rotation: {math.degrees(self.workspace.enaction.action.rotation_speed_rad):.1f}°/s"
        self.view.label3.text = label3
        label2 = f"Azimuth: {quaternion_to_azimuth(self.workspace.enaction.trajectory.body_quaternion):.0f}, " \
                 f"offset: ({self.workspace.memory.body_memory.compass_offset[0]:d}, " \
                 f"{self.workspace.memory.body_memory.compass_offset[1]:d}), " \
                 f"residual: {math.degrees(self.workspace.enaction.trajectory.body_direction_delta):.1f}"
        self.view.label2.text = label2

    def main(self, dt):
        """Update the body view every frame"""
        # The position of the robot in the view
        self.view.robot_rotate = 90 - self.workspace.memory.body_memory.body_azimuth()
        self.view.update_body_display(self.workspace.memory.body_memory)
        # Neurotransmitter display
        self.view.label_5HT.text = f"5-HT: {self.workspace.memory.body_memory.neurotransmitters[SEROTONIN]:d}"
        if self.workspace.memory.body_memory.neurotransmitters[SEROTONIN] >= 50:
            self.view.label_5HT.color = (0, 0, 0, 255)
        else:
            self.view.label_5HT.color = (255, 0, 0, 255)
        self.view.label_DA.text = f"DA: {self.workspace.memory.body_memory.neurotransmitters[DOPAMINE]:d}"
        if self.workspace.memory.body_memory.neurotransmitters[DOPAMINE] >= 50:
            self.view.label_DA.color = (0, 0, 0, 255)
        else:
            self.view.label_DA.color = (255, 0, 0, 255)
        self.view.label_NA.text = f"NA: {self.workspace.memory.body_memory.neurotransmitters[NORADRENALINE]:d}"
        if self.workspace.memory.body_memory.neurotransmitters[NORADRENALINE] >= 50:
            self.view.label_NA.color = (0, 0, 0, 255)
        else:
            self.view.label_NA.color = (255, 0, 0, 255)
        # Engagement mode display
        self.view.label1.text = f"Clock: {self.workspace.memory.clock} | " \
                                f"{ENGAGEMENT_MODES[self.workspace.engagement_mode]} | {self.workspace.decider_id}"
        # + ", En:{:d}%".format(self.workspace.memory.body_memory.energy) \
        # + ", Ex:{:d}%".format(self.workspace.memory.body_memory.excitation) \

        # At the end of interaction
        if self.workspace.enacter.interaction_step == ENACTION_STEP_RENDERING:
            self.update_labels()
            self.update_body_view()
