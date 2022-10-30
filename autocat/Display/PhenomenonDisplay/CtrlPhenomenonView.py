from pyrr import matrix44
from .PhenomenonView import PhenomenonView
from ..EgocentricDisplay.PointOfInterest import PointOfInterest
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FOCUS, EXPERIENCE_PLACE, EXPERIENCE_ALIGNED_ECHO


class CtrlPhenomenonView:
    """Handle the logic of the phenomenon view, retrieve data from the phenomenon and convert it
    to points of interest that can be displayed in a pyglet window"""
    def __init__(self, workspace):
        self.view = PhenomenonView()
        self.workspace = workspace
        self.egocentric_memory = workspace.memory.egocentric_memory
        self.points_of_interest = []
        self.last_used_id = -1
        self.phenomenon = None

        def on_text(text):
            """Send user keypress to the workspace to handle"""
            self.workspace.process_user_key(text)
            # if text.upper() == "A":
            #     self.workspace.put_decider_to_auto()
            # elif text.upper() == "M":
            #     self.workspace.put_decider_to_manual()
            # else:
            #     action = {"action": text}
            #     self.workspace.set_action(action)

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
        # TODO compute the robot's position relative to the phenomenon
        if self.phenomenon is not None:
            self.view.robot_pos_x = self.workspace.memory.allocentric_memory.robot_pos_x - self.phenomenon.x
            self.view.robot_pos_y = self.workspace.memory.allocentric_memory.robot_pos_y - self.phenomenon.y

    def update_points_of_interest(self, phenomenon):
        """Retrieve all the experiences in a phenomenon and create the corresponding points of interest"""
        for a in [elem for elem in phenomenon.affordances if elem.experience.id > self.last_used_id]:
            if a.experience.id > self.last_used_id:
                self.last_used_id = max(a.experience.id, self.last_used_id)
            poi = self.create_point_of_interest(a)
            self.points_of_interest.append(poi)

    def create_poi_focus(self):
        """Create a point of interest corresponding to the focus in the reference of the robot"""
        output = None
        if hasattr(self.workspace.agent, "focus"):
            if self.workspace.agent.is_focussed:
                x = self.workspace.agent.focus_xy[0]
                y = self.workspace.agent.focus_xy[1]
                output = PointOfInterest(x, y, self.view.robot_batch, self.view.foreground, EXPERIENCE_FOCUS)
        return output

    def create_point_of_interest(self, affordance):
        """Create a point of interest corresponding to the experience given as parameter"""
        x, y, _ = matrix44.apply_to_vector(affordance.position_matrix, [0., 0., 0.])
        poi = PointOfInterest(x, y, self.view.batch, self.view.foreground, affordance.experience.type,
                              experience=affordance.experience)

        # Show the position of the sensor
        points = affordance.sensor_triangle()
        if points is not None:
            self.view.add_polygon(points, "CadetBlue")

        return poi

    def main(self, dt):
        """Called every frame. Update the phenomenon view"""
        if self.workspace.flag_for_view_refresh:
            # Display in phenomenon view
            if len(self.workspace.integrator.phenomena) > 0:
                self.phenomenon = self.workspace.integrator.phenomena[0]
                self.update_points_of_interest(self.phenomenon)
            self.update_body_robot()
            self.workspace.flag_for_view_refresh = False  # Reset by CtrlBodyView
