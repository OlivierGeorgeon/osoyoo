import pyglet
from pyglet.window import key
from .PhenomenonView import PhenomenonView
from ..EgocentricDisplay.PointOfInterest import PointOfInterest, POINT_COMPASS
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FOCUS, EXPERIENCE_PLACE


class CtrlPhenomenonView:
    """Handle the logic of the egocentric view, retrieve data from the memory and convert it
    to points of interest that can be displayed in a pyglet window"""
    def __init__(self, workspace):
        self.view = PhenomenonView()
        self.workspace = workspace
        self.egocentric_memory = workspace.memory.egocentric_memory
        self.points_of_interest = []
        self.last_used_id = -1

        def on_text(text):
            """Handles user input"""
            if text.upper() == "A":
                self.workspace.put_decider_to_auto()
            elif text.upper() == "M":
                self.workspace.put_decider_to_manual()
            else:
                action = {"action": text}
                self.workspace.set_action(action)

        self.view.push_handlers(on_text)

    def add_point_of_interest(self, x, y, point_type, group=None, experience=None):
        """ Adding a point of interest to the view """
        if group is None:
            group = self.view.foreground
        point_of_interest = PointOfInterest(x, y, self.view.batch, group, point_type, experience=experience)
        self.points_of_interest.append(point_of_interest)
        return point_of_interest

    def update_body_robot(self):
        """Updates the robot's body to display by the egocentric view"""
        self.view.robot.rotate_head(self.workspace.memory.body_memory.head_direction_degree())
        self.view.azimuth = self.workspace.memory.body_memory.body_azimuth()

    def update_points_of_interest(self, phenomenon):
        """Retrieve all the experiences in a phenomenon and create the corresponding points of interest"""

        # Create the new points of interest from the new experiences
        for e in [elem for elem in phenomenon.experiences if elem.id > self.last_used_id]:
            if e.id > self.last_used_id:
                self.last_used_id = max(e.id, self.last_used_id)
            poi = self.create_point_of_interest(e)
            self.points_of_interest.append(poi)

    def create_poi_focus(self):
        """Create a point of interest corresponding to the focus in the reference of the robot"""
        output = None
        if hasattr(self.workspace.agent, "focus"):
            if self.workspace.agent.focus:
                x = self.workspace.agent.focus_xy[0]
                y = self.workspace.agent.focus_xy[1]
                output = PointOfInterest(x, y, self.view.robot_batch, self.view.foreground, EXPERIENCE_FOCUS)
        return output

    def create_point_of_interest(self, experience):
        """Create a point of interest corresponding to the experience given as parameter"""
        return PointOfInterest(experience.x, experience.y, self.view.batch, self.view.foreground,
                               experience.type, experience=experience)

    def main(self, dt):
        """Called every frame. Update the egocentric view"""
        if self.workspace.flag_for_view_refresh:
            self.update_points_of_interest()
            self.update_body_robot()
            # self.workspace.flag_for_view_refresh = False  # Reset by CtrlBodyView
