import pyglet
from pyglet.window import key
from .EgocentricView import EgocentricView
from .PointOfInterest import PointOfInterest, POINT_PROMPT
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FOCUS, EXPERIENCE_PLACE
from ...Workspace import INTERACTION_STEP_REFRESHING
from ...Decider.Action import ACTION_FORWARD, ACTION_LEFTWARD


class CtrlEgocentricView:
    """Handle the logic of the egocentric view, retrieve data from the memory and convert it
    to points of interest that can be displayed in a pyglet window"""
    def __init__(self, workspace):
        self.view = EgocentricView()
        self.workspace = workspace
        self.egocentric_memory = workspace.memory.egocentric_memory
        self.synthesizer = workspace.integrator
        self.points_of_interest = []
        self.last_action = None
        self.mouse_press_x = 0
        self.mouse_press_y = 0
        self.mouse_press_angle = 0
        # self.last_used_id = -1

        def on_mouse_press(x, y, button, modifiers):
            """ Selecting or unselecting points of interest """
            self.mouse_press_x, self.mouse_press_y, self.mouse_press_angle = \
                self.view.get_mouse_press_coordinate(x, y, button, modifiers)
            for p in self.points_of_interest:
                is_near = p.select_if_near(self.mouse_press_x, self.mouse_press_y)
                if is_near:
                    self.view.label_speed.text = "Clock: " + str(p.clock)

        def on_key_press(symbol, modifiers):
            """ Deleting or inserting points of interest """
            if symbol == key.DELETE:
                for p in self.points_of_interest:
                    if p.is_selected:
                        if p.experience is not None:
                            # Remove the corresponding experience from egocentric memory
                            self.egocentric_memory.experiences.remove(p.experience)
                        if p.type == POINT_PROMPT:
                            self.workspace.prompt_xy = None
                        p.delete()
                        self.points_of_interest.remove(p)
            if symbol == key.INSERT:
                # Set the agent's focus to the user prompt
                self.workspace.focus_xy = [self.mouse_press_x, self.mouse_press_y]
                # Mark the prompt
                self.workspace.prompt_xy = [self.mouse_press_x, self.mouse_press_y]
                focus_point = PointOfInterest(self.mouse_press_x, self.mouse_press_y, self.view.batch,
                                              self.view.background, POINT_PROMPT, self.workspace.clock)
                self.points_of_interest.append(focus_point)
                # focus_point.is_selected = True
                # focus_point.set_color('red')

        def on_text(text):
            """Send user keypress to the workspace to handle"""
            self.workspace.process_user_key(text)

        self.view.push_handlers(on_mouse_press, on_key_press, on_text)

    def add_point_of_interest(self, x, y, point_type, group=None, experience=None):
        """ Adding a point of interest to the view """
        if group is None:
            group = self.view.foreground
        point_of_interest = PointOfInterest(x, y, self.view.batch, group, point_type, self.workspace.clock, experience=experience)
        self.points_of_interest.append(point_of_interest)
        return point_of_interest

    def update_body_robot(self):
        """Updates the robot's body to display by the egocentric view"""
        self.view.robot.rotate_head(self.workspace.memory.body_memory.head_direction_degree())
        self.view.azimuth = self.workspace.memory.body_memory.body_azimuth()

    def update_points_of_interest(self):
        """Retrieve all new experiences from memory, create and update the corresponding points of interest"""

        # If timeout then no egocentric view update
        # if self.workspace.enacted_interaction['status'] == "T":
        #     print("No ego memory update")
        #     return

        # Create the new points of interest from the new experiences
        # new_experiences = [elem for elem in self.egocentric_memory.experiences if elem.id > self.last_used_id]
        new_experiences = [e for e in self.egocentric_memory.experiences if (e.clock >= self.workspace.clock - 1)]
        for e in new_experiences:
            # if e.id > self.last_used_id:
            #     self.last_used_id = max(e.id, self.last_used_id)
            poi = self.create_point_of_interest(e)
            self.points_of_interest.append(poi)

        displacement_matrix = self.workspace.enacted_interaction['displacement_matrix'] \

        # Displace the points of interest
        for poi_displace in self.points_of_interest:
            poi_displace.update(displacement_matrix)
            # Remove the agent's focus. It will be recreated if needed
            if poi_displace.type == EXPERIENCE_FOCUS:
                self.points_of_interest.remove(poi_displace)
                poi_displace.delete()

        # Mark the agent's focus
        poi_focus = self.create_poi_focus()
        if poi_focus is not None:
            self.points_of_interest.append(poi_focus)

        # Mark the new position
        self.add_point_of_interest(0, 0, EXPERIENCE_PLACE)

        # Make the points of interest fade out as they get older
        for poi_fade in self.points_of_interest:
            poi_fade.fade(self.workspace.clock)
        # Keep only the points of interest during their durability
        self.points_of_interest = [p for p in self.points_of_interest if p.clock + p.durability > self.workspace.clock]

    def create_poi_focus(self):
        """Create a point of interest corresponding to the focus"""
        agent_focus_point = None
        # if hasattr(self.workspace.agent, "is_focussed"):
        if self.workspace.focus_xy is not None:
            x = self.workspace.focus_xy[0]
            y = self.workspace.focus_xy[1]
            agent_focus_point = PointOfInterest(x, y, self.view.batch, self.view.foreground, EXPERIENCE_FOCUS, self.workspace.clock)
        return agent_focus_point

    def create_point_of_interest(self, experience):
        """Create a point of interest corresponding to the experience given as parameter"""
        return PointOfInterest(experience.x, experience.y, self.view.batch, self.view.foreground,
                               experience.type, self.workspace.clock, experience=experience)

    def main(self, dt):
        """Called every frame. Update the egocentric view"""
        # if self.workspace.flag_for_view_refresh:
        if self.workspace.interaction_step == INTERACTION_STEP_REFRESHING:
            self.update_points_of_interest()
            # self.workspace.flag_for_view_refresh = False  # Reset by CtrlBodyView

        # Update every frame to simulate the robot's displacement
        self.update_body_robot()
