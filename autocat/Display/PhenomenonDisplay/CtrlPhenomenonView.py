import math
from pyrr import matrix44
from .PhenomenonView import PhenomenonView
from ..EgocentricDisplay.PointOfInterest import PointOfInterest


class CtrlPhenomenonView:
    """Handle the logic of the phenomenon view, retrieve data from the phenomenon and convert it
    to points of interest that can be displayed in a pyglet window"""
    def __init__(self, workspace):
        self.view = PhenomenonView()
        self.workspace = workspace
        self.egocentric_memory = workspace.memory.egocentric_memory
        self.points_of_interest = []
        self.cones = []
        # self.last_used_id = -1
        self.phenomenon = None

        def on_text(text):
            """Handle user keypress"""
            if text.upper() == "R":
                self.phenomenon.confidence = max(0, self.phenomenon.confidence - 0.1)  # PHENOMENON_CONFIDENCE_LOW
            elif text.upper() == "P":
                self.phenomenon.confidence = min(self.phenomenon.confidence + 0.1, 1.)  # PHENOMENON_CONFIDENCE_HIGH
            else:
                # Other keypress are handled by the workspace
                self.workspace.process_user_key(text)

        def on_mouse_press(x, y, button, modifiers):
            """ Computing the position of the mouse click relative to the robot in mm and degrees """
            # window_press_x = (x - self.view.width / 2) * self.view.zoom_level * 2
            # window_press_y = (y - self.view.height / 2) * self.view.zoom_level * 2
            # angle = math.atan2(window_press_y, window_press_x)
            window_press_x, window_press_y, angle, _ = self.view.get_allocentric_coordinates(x, y)
            self.view.label.text = "Click: x:" + str(int(window_press_x)) + ", y:" + str(int(window_press_y)) \
                                   + ", angle:" + str(int(math.degrees(angle))) + "°."
            for p in self.points_of_interest:
                is_near = p.select_if_near(window_press_x, window_press_y)
                if is_near:
                    self.view.label_origin_direction.text = "Clock: " + str(p.clock)

        self.view.push_handlers(on_text, on_mouse_press)

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

        # Recreate all the points of interest
        for a in phenomenon.affordances:
            # if a.experience.id > self.last_used_id:
            #     self.last_used_id = max(a.experience.id, self.last_used_id)
            poi = self.create_point_of_interest(a)
            self.points_of_interest.append(poi)

        # Draw the phenomenon outline
        self.view.add_lines(phenomenon.convex_hull(), "black")

    def create_point_of_interest(self, affordance):
        """Create a point of interest corresponding to the affordance given as parameter"""
        # Create the point of interest at origin
        poi = PointOfInterest(0, 0, self.view.batch, self.view.forefront, affordance.experience.type, self.workspace.clock,
                              experience=affordance.experience)
        # Displace the point of interest to its position relative to the phenomenon and absolute direction
        poi.displace(matrix44.multiply(affordance.experience.rotation_matrix,
                                       matrix44.create_from_translation(affordance.point).astype('float64')))
        # Show the echo localization cone
        points = affordance.sensor_triangle()
        if points is not None:
            self.cones.append(self.view.add_polygon(points, "CadetBlue"))
        return poi

    def main(self, dt):
        """Called every frame. Update the phenomenon view"""
        if self.phenomenon is not None:
            self.view.label_confidence.text = "Confidence: " + str(round(self.phenomenon.confidence * 100)) + "%"
        if self.workspace.flag_for_view_refresh:
            # Display in phenomenon view
            # if len(self.workspace.integrator.phenomena) > 0:
            #     self.phenomenon = self.workspace.integrator.phenomena[0]
            if self.phenomenon is not None:
                self.update_points_of_interest(self.phenomenon)
                self.view.label_origin_direction.text = "Origin direction: " + \
                    str(round(math.degrees(self.phenomenon.origin_absolute_direction))) + "°. Nb tours:" + \
                    str(self.phenomenon.nb_tour)
            self.update_body_robot()
            self.workspace.flag_for_view_refresh = False  # Reset by CtrlBodyView
