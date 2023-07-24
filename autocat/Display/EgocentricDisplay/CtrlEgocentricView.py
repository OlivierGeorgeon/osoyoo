from pyglet.window import key
from .EgocentricView import EgocentricView
from ..PointOfInterest import PointOfInterest, POINT_PROMPT
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FOCUS
from ...Robot.CtrlRobot import INTERACTION_STEP_ENACTING, INTERACTION_STEP_REFRESHING


class CtrlEgocentricView:
    """Handle the logic of the egocentric view, retrieve data from the memory and convert it
    to points of interest that can be displayed in a pyglet window"""
    def __init__(self, workspace):
        self.view = EgocentricView()
        self.workspace = workspace
        self.synthesizer = workspace.integrator
        self.points_of_interest = []
        self.last_action = None
        self.click_point = None

        def on_mouse_press(x, y, button, modifiers):
            """ Selecting or unselecting points of interest """
            self.click_point = self.view.get_prompt_point(x, y, button, modifiers)
            for p in [p for p in self.points_of_interest if p.select_if_near(self.click_point)]:
                self.view.label2.text = "Point clock: " + str(p.clock)

        def on_key_press(symbol, modifiers):
            """ Deleting or inserting points of interest """
            if symbol == key.DELETE:
                # Remove the prompt
                self.workspace.memory.egocentric_memory.prompt_point = None
                # Remove the selected points
                for p in self.points_of_interest:
                    if p.is_selected or p.type == POINT_PROMPT:
                        p.delete()
                        self.points_of_interest.remove(p)
            if symbol == key.INSERT:
                # Remove the previous prompt
                for p in self.points_of_interest:
                    if p.type == POINT_PROMPT:
                        p.delete()
                        self.points_of_interest.remove(p)

                # Mark the new prompt
                self.workspace.memory.egocentric_memory.prompt_point = self.click_point
                focus_poi = PointOfInterest(self.click_point[0], self.click_point[1], self.view.batch,
                                            self.view.background, POINT_PROMPT, self.workspace.clock)
                self.points_of_interest.append(focus_poi)
                # focus_point.is_selected = True
                # focus_point.set_color('red')

        def on_text(text):
            """Send user keypress to the workspace to handle"""
            self.workspace.process_user_key(text)

        self.view.push_handlers(on_mouse_press, on_key_press, on_text)

    def update_body_robot(self):
        """Updates the robot's body to display by the egocentric view"""
        self.view.robot.rotate_head(self.workspace.memory.body_memory.head_direction_degree())
        self.view.azimuth = self.workspace.memory.body_memory.body_azimuth()

    def update_points_of_interest(self):
        """Retrieve all new experiences from memory, create and update the corresponding points of interest"""

        # Delete the points of interest
        self.points_of_interest = [p for p in self.points_of_interest if not p.delete()]

        # Recreate the points of interest from experiences
        for e in [e for e in self.workspace.memory.egocentric_memory.experiences.values()
                  if (e.clock + e.durability >= self.workspace.clock - 1)]:
            poi = PointOfInterest(0, 0, self.view.batch, self.view.forefront, e.type, e.clock,
                                  color_index=e.color_index)
            poi.displace(e.position_matrix)
            poi.fade(self.workspace.clock)
            self.points_of_interest.append(poi)

        # Re-create the focus point
        if self.workspace.memory.egocentric_memory.focus_point is not None:
            focus_poi = PointOfInterest(self.workspace.memory.egocentric_memory.focus_point[0],
                                        self.workspace.memory.egocentric_memory.focus_point[1],
                                        self.view.batch, self.view.forefront, EXPERIENCE_FOCUS, self.workspace.clock)
            self.points_of_interest.append(focus_poi)

        # Re-create the prompt point
        if self.workspace.memory.egocentric_memory.prompt_point is not None:
            prompt_poi = PointOfInterest(self.workspace.memory.egocentric_memory.prompt_point[0],
                                         self.workspace.memory.egocentric_memory.prompt_point[1],
                                         self.view.batch, self.view.background, POINT_PROMPT, self.workspace.clock)
            self.points_of_interest.append(prompt_poi)

    def main(self, dt):
        """Update the egocentric view"""

        # Update every frame to simulate the robot's displacement
        self.update_body_robot()

        # Update the display of egocentric memory
        if self.workspace.interaction_step in [INTERACTION_STEP_ENACTING, INTERACTION_STEP_REFRESHING]:
            self.update_points_of_interest()
