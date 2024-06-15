import math
from ..InteractiveDisplay import InteractiveDisplay
from ..PointOfInterest import PointOfInterest
from ...Robot.CtrlRobot import ENACTION_STEP_RENDERING


class CtrlPlaceCellView:
    """Handle the logic of the phenomenon view, retrieve data from the phenomenon and convert it
    to points of interest that can be displayed in a pyglet window"""
    def __init__(self, workspace):
        self.view = InteractiveDisplay()
        self.workspace = workspace
        self.cue_displays = []
        self.place_cell_id = -1
        self.selected_clock = 0

        def on_text(text):
            """Handle user keypress"""
            self.workspace.process_user_key(text)

        def on_mouse_press(x, y, button, modifiers):
            """ Computing the position of the mouse click relative to the place cell in mm and degrees """
            point = self.view.mouse_coordinates_to_point(x, y)
            angle = math.atan2(point[1], point[0])
            self.view.label2.text = f"Click: ({point[0]},{point[1]}), direction: {math.degrees(angle):.0f}°"
            selected_clocks = [p.clock for p in self.cue_displays if p.select_if_near(point)]
            if len(selected_clocks) > 0:
                self.selected_clock = selected_clocks[0]
                self.view.label1.text = f"Clock: {self.selected_clock}"

        self.view.push_handlers(on_text, on_mouse_press)

    def update_cue_displays(self):
        """Retrieve the new affordances in a phenomenon and create the corresponding points of interest"""
        if self.place_cell_id in self.workspace.memory.place_memory.place_cells:
            place_cell = self.workspace.memory.place_memory.place_cells[self.place_cell_id]

            # Delete all cue displays
            for cue_display in self.cue_displays:
                cue_display.delete()
            self.cue_displays = []

            # Recreate all cue displays
            for cue in place_cell.cues.values():
                cue_display = PointOfInterest(cue.pose_matrix, self.view.batch, self.view.forefront, cue.type,
                                              cue.clock, cue.color_index)
                self.cue_displays.append(cue_display)

            # Draw the cue outline if any
            # self.view.add_lines(phenomenon.outline(), "black")

    def main(self, dt):
        """Called every frame. Update the place cell view"""
        # The position of the robot in the view
        self.view.robot_rotate = 90 - self.workspace.memory.body_memory.body_azimuth()
        self.view.update_body_display(self.workspace.memory.body_memory)

        if self.place_cell_id in self.workspace.memory.place_memory.place_cells:
            place_cell = self.workspace.memory.place_memory.place_cells[self.place_cell_id]
            self.view.set_caption(f"Place Cell {self.place_cell_id} at {place_cell}")
            self.view.robot_translate = self.workspace.memory.allocentric_memory.robot_point - place_cell.point
            if self.workspace.enacter.interaction_step == ENACTION_STEP_RENDERING:
                self.update_cue_displays()
