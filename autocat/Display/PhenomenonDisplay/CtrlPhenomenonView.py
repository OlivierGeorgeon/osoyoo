from pyrr import matrix44
from .PhenomenonView import PhenomenonView
from ..EgocentricDisplay.PointOfInterest import PointOfInterest
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FOCUS


class CtrlPhenomenonView:
    """Handle the logic of the phenomenon view, retrieve data from the phenomenon and convert it
    to points of interest that can be displayed in a pyglet window"""
    def __init__(self, workspace):
        self.view = PhenomenonView()
        self.workspace = workspace
        self.egocentric_memory = workspace.memory.egocentric_memory
        self.points_of_interest = []
        self.cones = []
        self.last_used_id = -1
        self.phenomenon = None

        def on_text(text):
            """Handle user keypress"""
            if text.upper() == "R":
                self.phenomenon.confidence = max(0, self.phenomenon.confidence - 0.1)  # PHENOMENON_CONFIDENCE_LOW
            elif text.upper() == "P":
                self.phenomenon.confidence = min(1., self.phenomenon.confidence + 0.1)  # PHENOMENON_CONFIDENCE_HIGH
            else:
                # Other keypress are handled by the workspace
                self.workspace.process_user_key(text)

        self.view.push_handlers(on_text)

    # def add_point_of_interest(self, x, y, point_type, group=None, experience=None):
    #     """ Adding a point of interest to the view """
    #     if group is None:
    #         group = self.view.forefront
    #     point_of_interest = PointOfInterest(x, y, self.view.batch, group, point_type, experience=experience)
    #     self.points_of_interest.append(point_of_interest)
    #     return point_of_interest

    def update_body_robot(self):
        """Updates the robot's body to display by the egocentric view"""
        self.view.robot.rotate_head(self.workspace.memory.body_memory.head_direction_degree())
        self.view.azimuth = self.workspace.memory.body_memory.body_azimuth()
        # TODO compute the robot's position relative to the phenomenon
        if self.phenomenon is not None:
            self.view.robot_pos_x = self.workspace.memory.allocentric_memory.robot_pos_x - self.phenomenon.point[0]
            self.view.robot_pos_y = self.workspace.memory.allocentric_memory.robot_pos_y - self.phenomenon.point[1]

    def update_points_of_interest(self, phenomenon):
        """Retrieve the new affordances in a phenomenon and create the corresponding points of interest"""

        # Remove all the points of interest
        for poi in self.points_of_interest:
            poi.delete()
        self.points_of_interest = []
        for cone in self.cones:
            cone.delete()
        self.cones = []

        # for a in [elem for elem in phenomenon.affordances if elem.experience.id > self.last_used_id]:
        for a in phenomenon.affordances:
            if a.experience.id > self.last_used_id:
                self.last_used_id = max(a.experience.id, self.last_used_id)
            poi = self.create_point_of_interest(a)
            self.points_of_interest.append(poi)

        # Draw the phenomenon outline
        self.view.add_lines(phenomenon.convex_hull(), "black")

    # def create_poi_focus(self):
    #     """Create a point of interest corresponding to the focus in the reference of the robot"""
    #     output = None
    #     if hasattr(self.workspace.agent, "focus"):
    #         if self.workspace.agent.is_focussed:
    #             x = self.workspace.agent.focus_xy[0]
    #             y = self.workspace.agent.focus_xy[1]
    #             output = PointOfInterest(x, y, self.view.robot_batch, self.view.forefront, EXPERIENCE_FOCUS)
    #     return output

    def create_point_of_interest(self, affordance):
        """Create a point of interest corresponding to the affordance given as parameter"""
        # x, y, _ = matrix44.apply_to_vector(affordance.position_matrix, [0., 0., 0.])
        poi = PointOfInterest(0, 0, self.view.batch, self.view.forefront, affordance.experience.type,
                              experience=affordance.experience)
        # poi.displace(affordance.rotation_matrix)  # Rotate the shape on itself
        # poi.displace(affordance.position_matrix)  # and then translate
        # Rotate the shape on itself and then translate
        poi.displace(matrix44.multiply(affordance.experience.rotation_matrix,
                                       matrix44.create_from_translation(affordance.point).astype('float64')))
        # Show the position of the sensor
        points = affordance.sensor_triangle()
        if points is not None:
            self.cones.append(self.view.add_polygon(points, "CadetBlue"))
        return poi

    def main(self, dt):
        """Called every frame. Update the phenomenon view"""
        if self.phenomenon is not None:
            self.view.label_confidence.text = "Confidence: " + str(int(self.phenomenon.confidence * 100)) + "%"
        if self.workspace.flag_for_view_refresh:
            # Display in phenomenon view
            if len(self.workspace.integrator.phenomena) > 0:
                self.phenomenon = self.workspace.integrator.phenomena[0]
                self.update_points_of_interest(self.phenomenon)
            self.update_body_robot()
            self.workspace.flag_for_view_refresh = False  # Reset by CtrlBodyView
