import math
import numpy as np
from .PhenomenonView import PhenomenonView
from ..PointOfInterest import PointOfInterest, POINT_CONE
from ...Workspace import KEY_ENCLOSE
# from ...Robot.CtrlRobot import ENACTION_STEP_RENDERING
from ...Enaction import ENACTION_STEP_RENDERING
from ...Utils import quaternion_translation_to_matrix
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO
from ...Memory.PhenomenonMemory.PhenomenonMemory import TER


class CtrlPhenomenonView:
    """Handle the logic of the phenomenon view, retrieve data from the phenomenon and convert it
    to points of interest that can be displayed in a pyglet window"""
    def __init__(self, workspace):
        self.view = PhenomenonView()
        self.workspace = workspace
        self.affordance_displays = []
        self.phenomenon_id = -1
        self.selected_clock = 0
        self.view.label3.text = 'Type: None'

        def on_text(text):
            """Handle user keypress"""
            if self.phenomenon_id is not None and text.upper() == KEY_ENCLOSE:
                phenomenon = self.workspace.memory.phenomenon_memory.phenomena[self.phenomenon_id]
                if self.selected_clock > 0:
                    clock = self.selected_clock
                else:
                    clock = self.workspace.memory.clock
                affordances = [a for a in phenomenon.affordances.values() if a.clock == clock
                               and a.type == phenomenon.phenomenon_type]
                if len(affordances) > 0:
                    position_error = -affordances[0].point
                    phenomenon.enclose(position_error, clock)
                    workspace.memory.allocentric_memory.robot_point += position_error
                self.update_affordance_displays()
            else:
                # Other keypress are handled by the workspace
                self.workspace.process_user_key(text)

        def on_mouse_press(x, y, button, modifiers):
            """ Computing the position of the mouse click relative to the robot in mm and degrees """
            point = self.view.mouse_coordinates_to_point(x, y)
            angle = math.atan2(point[1], point[0])
            self.view.label2.text = f"Click: ({point[0]},{point[1]}), direction: {math.degrees(angle):.0f}°"
            selected_clocks = [p.clock for p in self.affordance_displays if p.select_if_near(point)]
            if len(selected_clocks) > 0:
                self.selected_clock = selected_clocks[0]
                self.view.label1.text = f"Clock: {self.selected_clock}"

        # Add the event functions to the view
        self.view.push_handlers(on_text, on_mouse_press)

        def on_mouse_scroll(x, y, dx, dy):
            """ Modify the phenomenon's confidence """
            # If scroll below the footer then modify the confidence
            if y < 50 and self.phenomenon_id in self.workspace.memory.phenomenon_memory.phenomena:
                # Modify the confidence
                phenomenon = self.workspace.memory.phenomenon_memory.phenomena[self.phenomenon_id]
                phenomenon.confidence += int(np.sign(dy))
                phenomenon.confidence = min(max(phenomenon.confidence, 0), 100)
            # If scroll above the footer then zoom
            else:
                self.view.zoom(dy)

        # Replace the window's scroll event function
        self.view.on_mouse_scroll = on_mouse_scroll

    def update_affordance_displays(self):
        """Retrieve the new affordances in a phenomenon and create the corresponding points of interest"""
        if self.phenomenon_id in self.workspace.memory.phenomenon_memory.phenomena:
            phenomenon = self.workspace.memory.phenomenon_memory.phenomena[self.phenomenon_id]

            # Delete the points of interest
            for poi in self.affordance_displays:
                poi.delete()
            self.affordance_displays = []

            # Recreate all affordance displays
            for a in phenomenon.affordances.values():
                ad = self.create_affordance_displays(a)
                self.affordance_displays.extend(ad)

            # Draw the phenomenon outline if any
            self.view.add_lines(phenomenon.outline(), "black")

    def create_affordance_displays(self, affordance):
        """Return the affordance displays for this affordance with the cone"""
        affordance_displays = []
        pose_matrix = quaternion_translation_to_matrix(affordance.quaternion, affordance.point)
        if affordance.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
            cone_display = PointOfInterest(pose_matrix, self.view.polar_batch, self.view.background, POINT_CONE,
                                           affordance.clock, affordance.color_index,
                                           np.linalg.norm(affordance.polar_sensor_point))
            affordance_displays.append(cone_display)
        poi = PointOfInterest(pose_matrix, self.view.polar_batch, self.view.forefront,
                              affordance.type, affordance.clock, affordance.color_index)
        affordance_displays.append(poi)
        return affordance_displays

    def main(self, dt):
        """Called every frame. Update the phenomenon view"""
        # The position of the robot in the view
        self.view.robot_rotate = 90 - self.workspace.memory.body_memory.body_azimuth()
        self.view.update_body_display(self.workspace.memory.body_memory)

        # Display Phenomenon 0 (terrain) by default if it exists
        if self.phenomenon_id is None and TER in self.workspace.memory.phenomenon_memory.phenomena:
            self.phenomenon_id = TER

        if self.phenomenon_id in self.workspace.memory.phenomenon_memory.phenomena:  # is not None:
            phenomenon = self.workspace.memory.phenomenon_memory.phenomena[self.phenomenon_id]
            self.view.robot_translate = self.workspace.memory.allocentric_memory.robot_point - phenomenon.point
            self.view.label3.text = f"Type: {phenomenon.phenomenon_type}, Confidence: {phenomenon.confidence}"
            if self.workspace.enacter.interaction_step == ENACTION_STEP_RENDERING:
                self.update_affordance_displays()
