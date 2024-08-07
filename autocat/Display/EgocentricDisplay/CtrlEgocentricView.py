import time
from pyrr import Matrix44
from pyglet.window import key, mouse
# from .EgocentricView import EgocentricView
from ..InteractiveDisplay import InteractiveDisplay
from ..PointOfInterest import PointOfInterest, POINT_PROMPT, POINT_ROBOT
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FOCUS, EXPERIENCE_ROBOT
from ...Robot.CtrlRobot import ENACTION_STEP_ENACTING, ENACTION_STEP_RENDERING


class CtrlEgocentricView:
    """Handle the logic of the egocentric view, retrieve data from the memory and convert it
    to points of interest that can be displayed in a pyglet window"""
    def __init__(self, workspace):
        self.view = InteractiveDisplay()
        self.view.set_caption("Egocentric " + workspace.robot_id)
        self.view.zoom_level = 2
        self.view.robot_rotate = 90  # Show the robot head up
        self.workspace = workspace
        self.points_of_interest = []
        self.last_action = None

        def on_mouse_press(x, y, button, modifiers):
            """ Selecting or unselecting points of interest """
            click_point = self.view.mouse_to_ego_point(x, y, button, modifiers)
            # Display select a point of interest and display its clock
            for p in [p for p in self.points_of_interest if p.select_if_near(click_point)]:
                self.view.label2.text = "Point clock: " + str(p.clock)

            if button == mouse.RIGHT:
                if modifiers & key.MOD_SHIFT:
                    # Delete the prompt
                    self.delete_prompt()
                else:
                    # Remove the previous prompt
                    for p in self.points_of_interest:
                        if p.type == POINT_PROMPT:
                            p.delete()
                            self.points_of_interest.remove(p)
                    # Mark the new prompt
                    self.workspace.memory.egocentric_memory.prompt_point = click_point
                    prompt_poi = PointOfInterest(Matrix44.from_translation(click_point).astype(float), self.view.egocentric_batch,
                                                 self.view.background, POINT_PROMPT, self.workspace.memory.clock, 0, 1, 0)
                    self.points_of_interest.append(prompt_poi)

        def on_key_press(symbol, modifiers):
            """ Delete the prompt and the selected points of interest """
            if symbol == key.DELETE:
                self.delete_prompt()

        def on_text(text):
            """Send user keypress to the workspace to handle"""
            self.workspace.process_user_key(text)

        self.view.push_handlers(on_mouse_press, on_key_press, on_text)

    def delete_prompt(self):
        """Delete the prompt"""
        print("delete prompt")
        self.workspace.memory.egocentric_memory.prompt_point = None
        # Remove the selected points
        for p in self.points_of_interest:
            if p.is_selected or p.type == POINT_PROMPT:
                p.delete()
                self.points_of_interest.remove(p)

    def update_points_of_interest(self):
        """Retrieve all new experiences from memory, create and update the corresponding points of interest"""

        # Delete the expired points of interest
        self.points_of_interest = [p for p in self.points_of_interest if not p.delete(self.workspace.enaction.clock)]

        # Displace the remaining points of interest
        start_time = time.time()
        for p in self.points_of_interest:
            displacement_matrix = self.workspace.enaction.trajectory.displacement_matrix
            p.displace(displacement_matrix)
            p.fade(self.workspace.memory.clock)
        # print(f"Displaced {len(self.points_of_interest):d} points of interest in {time.time() - start_time:.3f} seconds")

        # Create the new points of interest from the new experiences
        start_time = time.time()
        # es = [e for e in self.workspace.memory.egocentric_memory.experiences.values() if (e.clock + e.durability >= self.workspace.memory.clock - 1)]
        es = [e for e in self.workspace.memory.egocentric_memory.experiences.values() if e.clock == self.workspace.enaction.clock]
        for e in es:
            if e.type == EXPERIENCE_ROBOT:  # Draw the body of the other robot
                robot_shape = PointOfInterest(e.pose_matrix, self.view.egocentric_batch, self.view.background, POINT_ROBOT,
                                              e.clock)
                # robot_shape.fade(self.workspace.memory.clock)
                self.points_of_interest.append(robot_shape)
            poi = PointOfInterest(e.pose_matrix, self.view.egocentric_batch, self.view.forefront, e.type, e.clock,
                                  e.color_index, e.durability, 0)
            # poi.fade(self.workspace.memory.clock)
            self.points_of_interest.append(poi)
        # print(f"Created {len(es):d} new points of interest in {time.time() - start_time:.3f} seconds")

        # Re-create the focus point with durability of 1
        if self.workspace.memory.egocentric_memory.focus_point is not None:
            p = Matrix44.from_translation(self.workspace.memory.egocentric_memory.focus_point).astype(float)
            focus_poi = PointOfInterest(p, self.view.egocentric_batch, self.view.forefront, EXPERIENCE_FOCUS,
                                        self.workspace.memory.clock, 0, 1, 0)
            self.points_of_interest.append(focus_poi)

        # Re-create the prompt point with durability of 1
        if self.workspace.memory.egocentric_memory.prompt_point is not None:
            p = Matrix44.from_translation(self.workspace.memory.egocentric_memory.prompt_point.astype(float))
            prompt_poi = PointOfInterest(p, self.view.egocentric_batch, self.view.background, POINT_PROMPT,
                                         self.workspace.memory.clock, 0, 1, 0)
            self.points_of_interest.append(prompt_poi)

    def reset(self):
        """Reset all the points of interest"""
        # TODO Reload the points of interest from the experiences
        for poi in self.points_of_interest:
            poi.delete()
        self.points_of_interest = []

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
            self.update_points_of_interest()
