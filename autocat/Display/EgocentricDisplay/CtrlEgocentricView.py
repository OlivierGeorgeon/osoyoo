import time
import math
from pyrr import Matrix44
from pyglet.window import key, mouse
from ..ShapeDisplay import ShapeDisplay, POINT_PROMPT, POINT_ROBOT
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FOCUS, EXPERIENCE_ROBOT
from ...Enaction import ENACTION_STEP_RENDERING
from ..CtrlWindow import CtrlWindow


class CtrlEgocentricView(CtrlWindow):
    """Handle the logic of the egocentric view, retrieve data from the memory and convert it
    to points of interest that can be displayed in a pyglet window"""
    def __init__(self, workspace):
        super().__init__(workspace)
        self.view.set_caption("Egocentric " + workspace.robot_id)
        self.view.zoom_level = 2
        self.view.robot_rotate = 90  # Show the robot head up
        self.points_of_interest = []
        self.prompt_shape = None

        def on_mouse_press(x, y, button, modifiers):
            """ Selecting or unselecting points of interest """
            click_point = self.view.window_to_ego_centric(x, y)
            # Right click: insert a prompt
            if button == mouse.RIGHT:
                self.workspace.memory.egocentric_memory.prompt_point = click_point
                self.update_prompt()
                allo_point = self.workspace.memory.egocentric_to_allocentric(click_point)
                self.workspace.memory.allocentric_memory.update_prompt(allo_point, self.workspace.memory.clock)
            # Left click: select a point of interest
            else:
                for p in [p for p in self.points_of_interest if p.select_if_near(click_point)]:
                    self.view.label2.text = "Clock: " + str(p.clock)

        def on_key_press(symbol, modifiers):
            """ Delete the prompt """
            if symbol == key.DELETE:
                self.workspace.memory.egocentric_memory.prompt_point = None
                self.update_prompt()
                self.workspace.memory.allocentric_memory.update_prompt(None, self.workspace.memory.clock)

        self.view.push_handlers(on_mouse_press, on_key_press)

    def move_and_add_shapes(self):
        """Retrieve new experiences from memory, create corresponding points of interest, move and fade the previous"""

        # Delete the expired points of interest
        self.points_of_interest = [p for p in self.points_of_interest if not p.delete(self.workspace.enaction.clock)]

        # Displace the remaining points of interest
        start_time = time.time()
        for p in self.points_of_interest:
            displacement_matrix = self.workspace.enaction.trajectory.displacement_matrix
            p.displace(displacement_matrix)
            p.fade(self.workspace.memory.clock)
        # print(f"Displaced {len(self.points_of_interest):d} points of interest in {time.time() -
        # start_time:.3f} seconds")

        # Create the new points of interest from the new experiences
        start_time = time.time()
        es = [e for e in self.workspace.memory.egocentric_memory.experiences.values()
              if e.clock == self.workspace.enaction.clock]
        for e in es:
            if e.type == EXPERIENCE_ROBOT:  # Draw the body of the other robot
                robot_shape = ShapeDisplay(e.pose_matrix, self.view.egocentric_batch, self.view.background, POINT_ROBOT,
                                           e.clock)
                # robot_shape.fade(self.workspace.memory.clock)
                self.points_of_interest.append(robot_shape)
            poi = ShapeDisplay(e.pose_matrix, self.view.egocentric_batch, self.view.forefront, e.type, e.clock,
                               e.color_index, e.durability, 0)
            self.points_of_interest.append(poi)
        # print(f"Created {len(es):d} new points of interest in {time.time() - start_time:.3f} seconds")

        # Re-create the focus point with durability of 1
        if self.workspace.memory.egocentric_memory.focus_point is not None:
            p = Matrix44.from_translation(self.workspace.memory.egocentric_memory.focus_point).astype(float)
            focus_poi = ShapeDisplay(p, self.view.egocentric_batch, self.view.forefront, EXPERIENCE_FOCUS,
                                     self.workspace.enaction.clock, 0, 1, 0)
            self.points_of_interest.append(focus_poi)

    def update_prompt(self):
        """Delete and recreate the prompt"""
        # Delete the prompt shape
        if self.prompt_shape is not None:
            self.prompt_shape.delete()
            self.prompt_shape = None
        # Re-create the prompt shape
        if self.workspace.memory.egocentric_memory.prompt_point is not None:
            p = Matrix44.from_translation(self.workspace.memory.egocentric_memory.prompt_point.astype(float))
            self.prompt_shape = ShapeDisplay(p, self.view.egocentric_batch, self.view.background, POINT_PROMPT,
                                             self.workspace.memory.clock, 0, 0, 0)

    def reset(self):
        """Reset all the points of interest"""
        # TODO Reload the points of interest from the experiences
        for poi in self.points_of_interest:
            poi.delete()
        self.points_of_interest = []
        self.update_prompt()

    def display_mouse(self, ego_point):
        """Display the mouse information"""
        ego_angle = math.degrees(math.atan2(ego_point[1], ego_point[0]))
        allo_point = self.workspace.memory.egocentric_to_allocentric(ego_point)
        self.view.label3.text = f"Ego: {tuple(ego_point[0:2])}, {ego_angle:.0f}°. " \
                                f"Allo: {tuple(allo_point[:2].astype(int))}"

    def main(self, dt):
        """Update the egocentric view"""
        # If back from imaginary mode, reset the view
        if self.workspace.enacter.view_reset_flag:
            self.reset()
        # Update every frame to simulate the robot's displacement
        self.view.update_body_display(self.workspace.memory.body_memory)
        self.view.egocentric_rotate = -self.workspace.memory.body_memory.simulation_rotation_deg
        self.view.egocentric_translate = -self.workspace.memory.body_memory.simulation_translate
        # Update every interaction cycle to update the experiences
        if self.workspace.enacter.interaction_step in [ENACTION_STEP_RENDERING]:
            self.move_and_add_shapes()
            self.update_prompt()
