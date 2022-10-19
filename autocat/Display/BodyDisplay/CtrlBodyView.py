import pyglet
from pyrr import matrix44
import math
from .BodyView import BodyView
from ..EgocentricDisplay.PointOfInterest import PointOfInterest, POINT_COMPASS


class CtrlBodyView:
    """Handle the logic of the egocentric view, retrieve data from the memory and convert it
    to points of interest that can be displayed in a pyglet window"""

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

    def update_body_robot(self):
        """Updates the robot's body to display by the egocentric view"""
        self.view.robot.rotate_head(self.workspace.memory.body_memory.head_direction_degree())
        self.view.azimuth = self.workspace.memory.body_memory.body_azimuth()
        self.view.label.text += ", estimated: " + str(self.view.azimuth) + "°"

    def update_points_of_interest(self):
        """Add and update points of interest from the latest enacted interaction """

        # If timeout then no body view update
        if self.workspace.enacted_interaction['status'] == "T":
            print("No body memory update")
            return

        # Rotate the previous compass points so they remain at the south of the view
        yaw = self.workspace.enacted_interaction['yaw']
        displacement_matrix = matrix44.create_from_z_rotation(math.radians(yaw))
        for poi_displace in self.points_of_interest:
            poi_displace.update(displacement_matrix)

        # Add the new compass point
        if 'azimuth' in self.workspace.enacted_interaction:
            self.add_point_of_interest(self.workspace.enacted_interaction['compass_x'],
                                       self.workspace.enacted_interaction['compass_y'], POINT_COMPASS)
            self.view.label.text = "Azimuth measured: " + str(self.workspace.enacted_interaction['azimuth']) + "°"
        else:
            self.view.label.text = "Azimuth measured: None"

        # Make the points of interest fade out using the durability of the given interaction
        if len(self.points_of_interest) > 0:
            for poi_fade in self.points_of_interest:
                if poi_fade is not None and poi_fade.experience is not None:

                    if isinstance(poi_fade.shape, pyglet.graphics.vertexdomain.IndexedVertexList):
                        for s in poi_fade.shape.colors:
                            # print("sssddfsfsf " ,s)
                            # s.opacity = poi.interaction.durability * 10
                            # print("opacity : ",s.opacity)
                            # TODO : CHANGE OPACITY OF VERTEX LIST
                            ''
                    else:
                        poi_fade.shape.opacity = min(
                            poi_fade.experience.actual_durability * (255 / poi_fade.experience.durability), 255)
                    if poi_fade.experience.actual_durability <= 0:
                        poi_fade.delete()
                        self.points_of_interest.remove(poi_fade)

    def main(self, dt):
        """Called every frame. Update the body view"""
        if self.workspace.flag_for_view_refresh:
            self.update_points_of_interest()
            self.update_body_robot()
            self.workspace.flag_for_view_refresh = False
