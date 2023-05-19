import math
from pyrr import matrix44
from .PhenomenonView import PhenomenonView
from .AffordanceDisplay import AffordanceDisplay
from ...Workspace import KEY_DECREASE_CONFIDENCE, KEY_INCREASE_CONFIDENCE
from ...Robot.CtrlRobot import INTERACTION_STEP_IDLE, INTERACTION_STEP_REFRESHING


class CtrlPhenomenonView:
    """Handle the logic of the phenomenon view, retrieve data from the phenomenon and convert it
    to points of interest that can be displayed in a pyglet window"""
    def __init__(self, workspace):
        self.view = PhenomenonView()
        self.workspace = workspace
        self.egocentric_memory = workspace.memory.egocentric_memory
        self.affordance_displays = []
        self.phenomenon = None

        def on_text(text):
            """Handle user keypress"""
            if text.upper() == KEY_DECREASE_CONFIDENCE:
                self.phenomenon.confidence = max(0, self.phenomenon.confidence - 0.1)  # PHENOMENON_CONFIDENCE_LOW
            elif text.upper() == KEY_INCREASE_CONFIDENCE:
                self.phenomenon.confidence = min(self.phenomenon.confidence + 0.1, 1.)  # PHENOMENON_CONFIDENCE_HIGH
            else:
                # Other keypress are handled by the workspace
                self.workspace.process_user_key(text)

        def on_mouse_press(x, y, button, modifiers):
            """ Computing the position of the mouse click relative to the robot in mm and degrees """
            point = self.view.mouse_coordinates_to_point(x, y)
            angle = math.atan2(point[1], point[0])
            self.view.label1.text = "Click: x:" + str(round(point[0])) + ", y:" + str(round(point[1])) \
                                    + ", angle:" + str(round(math.degrees(angle))) + "°."
            for p in [p for p in self.affordance_displays if p.select_if_near(point)]:
                self.view.label3.text = "Clock: " + str(p.clock)

        self.view.push_handlers(on_text, on_mouse_press)

    def update_body_robot(self):
        """Updates the robot's body to display by the phenomenon view"""
        self.view.robot.rotate_head(self.workspace.memory.body_memory.head_direction_degree())
        if self.phenomenon is not None:
            self.view.phenomenon_point = self.phenomenon.point

    def update_affordance_displays(self, phenomenon):
        """Retrieve the new affordances in a phenomenon and create the corresponding points of interest"""

        # Delete the points of interest
        # Crash seem to try to delete twice the shape
        # self.affordance_displays = [p for p in self.affordance_displays if not p.delete()]
        for poi in self.affordance_displays:
            poi.delete()
        self.affordance_displays = []

        # Recreate all affordance displays
        for a in phenomenon.affordances.values():
            ad = self.create_affordance_display(a)
            self.affordance_displays.append(ad)

        # Draw the phenomenon outline
        self.view.add_lines(phenomenon.convex_hull(), "black")

    def create_affordance_display(self, affordance):
        """Create a point of interest corresponding to the affordance given as parameter"""
        # Create the point of interest at origin
        poi = AffordanceDisplay(0, 0, self.view.batch, self.view.forefront, self.view.background,
                                affordance.experience.type, affordance.experience.clock, affordance.experience.color_index)
        # Displace the point of interest to its position relative to the phenomenon and absolute direction
        poi.displace(matrix44.multiply(affordance.experience.rotation_matrix,
                                       matrix44.create_from_translation(affordance.point).astype('float64')))
        # Show the echo localization cone
        points = affordance.sensor_triangle()
        # if the affordance has a polygon then add it to the AffordanceDisplay
        if points is not None:
            poi.add_cone(points, "CadetBlue")
        return poi

    def main(self, dt):
        """Called every frame. Update the phenomenon view"""
        # The position of the robot in the view
        self.view.robot_rotate = 90 - self.workspace.memory.body_memory.body_azimuth()
        # Always display Phenomenon 0 (terrain)
        if 0 in self.workspace.memory.phenomenon_memory.phenomena:
            self.phenomenon = self.workspace.memory.phenomenon_memory.phenomena[0]

        if self.phenomenon is not None:
            self.view.robot_translate = self.workspace.memory.allocentric_memory.robot_point - self.phenomenon.point
            self.view.label2.text = "Confidence: " + str(round(self.phenomenon.confidence * 100)) + "%"
        if self.workspace.interaction_step == INTERACTION_STEP_REFRESHING:
            if self.phenomenon is not None:
                self.update_affordance_displays(self.phenomenon)
                self.view.label3.text = self.phenomenon.phenomenon_label()
            self.update_body_robot()
