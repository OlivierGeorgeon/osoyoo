from pyrr import matrix44
import math
from .BodyView import BodyView
from ..EgocentricDisplay.PointOfInterest import PointOfInterest, POINT_COMPASS, POINT_AZIMUTH


class CtrlBodyView:
    """Controls the body view"""
    def __init__(self, workspace):
        self.view = BodyView()
        self.workspace = workspace
        self.points_of_interest = []
        self.last_action = None
        self.mouse_press_x = 0
        self.mouse_press_y = 0
        self.mouse_press_angle = 0
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

    def add_point_of_interest(self, x, y, point_type, group=None):
        """ Adding a point of interest to the view """
        if group is None:
            group = self.view.foreground
        point_of_interest = PointOfInterest(x, y, self.view.batch, group, point_type, experience=None)
        self.points_of_interest.append(point_of_interest)

    def update_body_view(self):
        """Add and update points of interest from the latest enacted interaction """

        # If timeout then no body view update
        if self.workspace.enacted_interaction['status'] == "T":
            print("No body memory update")
            return

        # Update the position of the robot
        self.view.robot.rotate_head(self.workspace.memory.body_memory.head_direction_degree())
        self.view.azimuth = self.workspace.memory.body_memory.body_azimuth()
        self.view.body_rotation_matrix = self.workspace.memory.body_memory.body_direction_matrix()

        # Rotate the previous compass points so they remain at the south of the view
        yaw = self.workspace.enacted_interaction['yaw']
        displacement_matrix = matrix44.create_from_z_rotation(math.radians(yaw))
        for poi in [p for p in self.points_of_interest if p.type == POINT_COMPASS]:
            poi.update(displacement_matrix)

        # Add the new points that indicate the south relative to the robot
        if 'compass_x' in self.workspace.enacted_interaction:
            self.add_point_of_interest(self.workspace.enacted_interaction['compass_x'],
                                       self.workspace.enacted_interaction['compass_y'], POINT_COMPASS)
            self.add_point_of_interest(self.workspace.enacted_interaction['compass_x'],
                                       self.workspace.enacted_interaction['compass_y'], POINT_AZIMUTH,
                                       self.view.background)
            self.view.label.text = "Azimuth compass: " + str(self.workspace.enacted_interaction['azimuth']) + "°"
        else:
            self.view.azimuth = self.workspace.memory.body_memory.body_azimuth()
            x = 300 * math.cos(math.radians(self.view.azimuth + 180))
            y = 300 * math.sin(math.radians(self.view.azimuth + 180))
            self.add_point_of_interest(x, y, POINT_COMPASS)
            x = 330 * math.cos(math.radians(self.view.azimuth + 180))
            y = 330 * math.sin(math.radians(self.view.azimuth + 180))
            self.add_point_of_interest(x, y, POINT_AZIMUTH, self.view.background)
            self.view.label.text = "Azimuth compass: None"

        self.view.label.text += ", corrected: " + str(self.view.azimuth) + "°"

        # Fade the points of interest
        for poi in self.points_of_interest:
            poi.fade()

    def main(self, dt):
        """Called every frame. Update the body view"""
        if self.workspace.flag_for_view_refresh:
            self.update_body_view()
            # self.update_body_robot()
            self.workspace.flag_for_view_refresh = False
