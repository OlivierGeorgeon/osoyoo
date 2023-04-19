from pyglet.window import key
from .EgocentricView import EgocentricView
from autocat.Display.PointOfInterest import PointOfInterest, POINT_PROMPT
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FOCUS, EXPERIENCE_PLACE
from ...Workspace import INTERACTION_STEP_REFRESHING, INTERACTION_STEP_ENACTING


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

    def add_point_of_interest(self, x, y, point_type, group=None):
        """ Adding a point of interest to the view """
        if group is None:
            group = self.view.forefront
        point_of_interest = PointOfInterest(x, y, self.view.batch, group, point_type, self.workspace.clock)
        self.points_of_interest.append(point_of_interest)
        return point_of_interest

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
            # if e.color is not None:
            #     poi.color = e.color
            poi.displace(e.position_matrix)
            poi.fade(self.workspace.clock)
            self.points_of_interest.append(poi)

        # Re-create the focus point
        poi_focus = self.create_poi_focus()
        if poi_focus is not None:
            self.points_of_interest.append(poi_focus)

        # Re-create the prompt point
        if self.workspace.memory.egocentric_memory.prompt_point is not None:
            prompt_poi = PointOfInterest(self.workspace.memory.egocentric_memory.prompt_point[0], self.workspace.memory.egocentric_memory.prompt_point[1],
                                         self.view.batch, self.view.background, POINT_PROMPT, self.workspace.clock)
            self.points_of_interest.append(prompt_poi)

    def create_poi_focus(self):
        """Create a point of interest corresponding to the focus"""
        agent_focus_point = None
        if self.workspace.memory.egocentric_memory.focus_point is not None:
            x = self.workspace.memory.egocentric_memory.focus_point[0]
            y = self.workspace.memory.egocentric_memory.focus_point[1]
            print("Focus point created", x, y)
            agent_focus_point = PointOfInterest(x, y, self.view.batch, self.view.forefront, EXPERIENCE_FOCUS,
                                                self.workspace.clock)
        return agent_focus_point

    def main(self, dt):
        """Called every frame. Update the egocentric view"""

        if self.workspace.interaction_step == INTERACTION_STEP_ENACTING:
            self.update_points_of_interest()

        # Update during simulation and at the end of the interaction cicle
        if self.workspace.interaction_step == INTERACTION_STEP_REFRESHING:
            self.update_points_of_interest()

        # Update every frame to simulate the robot's displacement
        self.update_body_robot()
