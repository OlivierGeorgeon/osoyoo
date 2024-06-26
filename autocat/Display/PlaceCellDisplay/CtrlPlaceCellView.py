import math
import numpy as np
from webcolors import name_to_rgb
from pyglet.gl import GL_LINES
from ..InteractiveDisplay import InteractiveDisplay
from ..PointOfInterest import PointOfInterest
from ...Robot.CtrlRobot import ENACTION_STEP_RENDERING
from ...Memory.EgocentricMemory.Experience import FLOOR_COLORS


class CtrlPlaceCellView:
    """Handle the logic of the phenomenon view, retrieve data from the phenomenon and convert it
    to points of interest that can be displayed in a pyglet window"""
    def __init__(self, workspace):
        self.view = InteractiveDisplay()
        self.workspace = workspace
        self.cue_displays = []
        self.place_cell_id = 0
        self.selected_clock = 0
        self.graph_display = None
        self.echo_curve = None

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
            for cue in place_cell.cues:
                cue_display = PointOfInterest(cue.pose_matrix, self.view.polar_batch, self.view.forefront, cue.type,
                                              cue.clock, cue.color_index)
                self.cue_displays.append(cue_display)

            # Draw the graph of place cells
            if self.graph_display is not None:
                self.graph_display.delete()
                self.graph_display = None
            points = []
            for u, v in self.workspace.memory.place_memory.place_cell_graph.edges:
                points.append(self.workspace.memory.place_memory.place_cells[u].point)
                points.append(self.workspace.memory.place_memory.place_cells[v].point)
            nb = len(points)
            if nb > 0:
                index = list(range(nb))
                points = np.array(points) - place_cell.point
                li = points[:, 0:2].flatten().astype("int").tolist()
                self.graph_display = self.view.polar_batch.add_indexed(nb, GL_LINES, self.view.forefront, index, ('v2i', li),
                                                                       ('c4B', nb * (*name_to_rgb(FLOOR_COLORS[0]), 255)))

            # Draw the echo curve
            if self.echo_curve is not None:
                self.echo_curve.delete()
                self.echo_curve = None
            points = place_cell.cartesian_echo_curve
            nb = points.shape[0]
            index = []
            for i in range(0, nb - 1):
                index.extend([i, i + 1])
            li = points[:, 0:2].flatten().astype("int").tolist()
            self.echo_curve = self.view.polar_batch.add_indexed(nb, GL_LINES, self.view.forefront, index, ('v2i', li),
                                                                ('c4B', nb * (*name_to_rgb("orange"), 255)))

    def main(self, dt):
        """Called every frame. Update the place cell view"""
        # The position of the robot in the view
        self.view.robot_rotate = 90 - self.workspace.memory.body_memory.body_azimuth()
        self.view.update_body_display(self.workspace.memory.body_memory)

        if self.place_cell_id in self.workspace.memory.place_memory.place_cells:
            place_cell = self.workspace.memory.place_memory.place_cells[self.place_cell_id]
            # self.view.set_caption(f"Place Cell {self.place_cell_id} at {place_cell}")
            self.view.robot_translate = self.workspace.memory.allocentric_memory.robot_point - place_cell.point
            if self.workspace.enacter.interaction_step == ENACTION_STEP_RENDERING:
                self.update_cue_displays()
