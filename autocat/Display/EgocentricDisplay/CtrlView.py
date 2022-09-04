import pyglet
from pyglet.window import key
from .EgocentricView import EgocentricView
from .PointOfInterest import *
from ...Workspace import Workspace
from ...CtrlWorkspace import CtrlWorkspace


class CtrlView:
    """Handle the logic of the egocentric view, retrieve data from the memory and convert it
    to points of interest that can be displayed in a pyglet window"""
    def __init__(self, ctrl_workspace):
        self.view = EgocentricView()
        self.ctrl_workspace = ctrl_workspace
        self.memory = ctrl_workspace.workspace.egocentric_memory
        self.synthesizer = ctrl_workspace.synthesizer
        self.points_of_interest = []
        self.last_action = None
        self.mouse_press_x = 0
        self.mouse_press_y = 0
        self.mouse_press_angle = 0
        self.last_used_id = -1

        def on_mouse_press(x, y, button, modifiers):
            """ Selecting or unselecting points of interest """
            self.mouse_press_x, self.mouse_press_y, self.mouse_press_angle = \
                self.view.get_mouse_press_coordinate(x, y, button, modifiers)
            for p in self.points_of_interest:
                p.select_if_near(self.mouse_press_x, self.mouse_press_y)

        def on_key_press(symbol, modifiers):
            """ Deleting or inserting points of interest """
            if symbol == key.DELETE:
                for p in self.points_of_interest:
                    if p.is_selected:
                        p.delete()
                        self.points_of_interest.remove(p)
                        if p.interaction is not None:
                            self.memory.interactions.remove(p.interaction)
            if symbol == key.INSERT:
                phenomenon = PointOfInterest(self.mouse_press_x, self.mouse_press_y, self.view.batch,
                                             self.view.background, EXPERIENCE_FOCUS)
                self.points_of_interest.append(phenomenon)
                phenomenon.is_selected = True
                phenomenon.set_color('red')

        self.view.push_handlers(on_mouse_press, on_key_press)

    def add_point_of_interest(self, x, y, point_type, group=None, interaction=None):
        """ Adding a point of interest to the view """
        if group is None:
            group = self.view.foreground
        point_of_interest = PointOfInterest(x, y, self.view.batch, group, point_type, interaction=interaction)
        self.points_of_interest.append(point_of_interest)
        return point_of_interest

    def update_points_of_interest(self):
        """Retrieve all new interactions from the memory, create corresponding points of interest
        then update the shape of each POI"""

        # If timeout then no egocentric view update
        if self.ctrl_workspace.enacted_interaction['status'] == "T":
            print("No ego memory update")
            return

        # Create the new points of interest from the new experiences
        new_experiences = [elem for elem in self.memory.interactions if elem.id > self.last_used_id]
        for interaction in new_experiences:
            if interaction.id > self.last_used_id:
                self.last_used_id = max(interaction.id, self.last_used_id)
            poi = self.create_point_of_interest(interaction)
            self.points_of_interest.append(poi)

        # The points of interest Central Echo from the list in the synthesizer
        for experience_central_echo in self.synthesizer.experiences_central_echo:
            poi_central_echo = self.create_point_of_interest(experience_central_echo)
            # print(poi_central_echo)
            self.points_of_interest.append(poi_central_echo)

        displacement_matrix = self.ctrl_workspace.enacted_interaction['displacement_matrix'] if 'displacement_matrix' \
            in self.ctrl_workspace.enacted_interaction else None

        # Displace the points of interest
        for poi_displace in self.points_of_interest:
            if poi_displace.type != POINT_COMPASS:  # Do not displace the compass points
                poi_displace.update(displacement_matrix)
            if poi_displace.type == EXPERIENCE_FOCUS:
                self.points_of_interest.remove(poi_displace)
                poi_displace.delete()

        # Mark the new position
        self.add_point_of_interest(0, 0, POINT_PLACE)

        # Update the robot's position
        self.view.robot.rotate_head(self.ctrl_workspace.enacted_interaction['head_angle'])
        self.view.azimuth = self.ctrl_workspace.enacted_interaction['azimuth']

        # Point of interest compass
        # if 'compass_x' in self.ctrl_workspace.enacted_interaction:
        #     self.add_point_of_interest(self.ctrl_workspace.enacted_interaction['compass_x'],
        #                                self.ctrl_workspace.enacted_interaction['compass_y'], POINT_COMPASS)

        # Point of interest focus
        poi_focus = self.create_poi_focus()
        if poi_focus is not None:
            self.points_of_interest.append(poi_focus)

        # Make the points of interest fade out using the durability of the given interaction
        if len(self.points_of_interest) > 0:
            for poi_fade in self.points_of_interest:
                if poi_fade is not None and poi_fade.interaction is not None:
                    
                    if isinstance(poi_fade.shape, pyglet.graphics.vertexdomain.IndexedVertexList):
                        for s in poi_fade.shape.colors:
                            #print("sssddfsfsf " ,s)
                            #s.opacity = poi.interaction.durability * 10
                            #print("opacity : ",s.opacity)
                            # TODO : CHANGE OPACITY OF VERTEX LIST
                            ''
                    else:
                        poi_fade.shape.opacity = min(poi_fade.interaction.actual_durability * (255/poi_fade.interaction.durability), 255)
                    if poi_fade.interaction.actual_durability <= 0:
                        poi_fade.delete()
                        self.points_of_interest.remove(poi_fade)

    def create_poi_focus(self):
        """Create a point of interest corresponding to the focus"""
        output = None
        if hasattr(self.ctrl_workspace.agent, "focus"):
            if self.ctrl_workspace.agent.focus:
                x = self.ctrl_workspace.agent.echo_xy[0]
                y = self.ctrl_workspace.agent.echo_xy[1]
                output = PointOfInterest(x, y, self.view.batch, self.view.foreground, EXPERIENCE_FOCUS)
        return output

    def create_point_of_interest(self, interaction):
        """Create a point of interest corresponding to the interaction given as parameter"""
        return PointOfInterest(interaction.x, interaction.y, self.view.batch, self.view.foreground,
                               interaction.type, interaction=interaction)

    def get_focus_phenomenon(self):
        """ Returning the first selected phenomenon """
        for p in self.points_of_interest:
            if p.type == EXPERIENCE_FOCUS:
                return p
        return None

    def main(self, dt):
        """Called every frame, update the view"""
        if self.ctrl_workspace.flag_for_view_refresh:
            # self.points_of_interest = []
            self.update_points_of_interest()
            # if self.synthesizer is not None and len(self.synthesizer.last_real_echos) > 0:
            #     last_real_echos = []
            self.ctrl_workspace.flag_for_view_refresh = False


# Displaying EgocentricView with points of interest.
# Allow selecting points of interest and inserting and deleting phenomena
# py -m stage_titouan.Display.EgocentricDisplay.CtrlView
if __name__ == "__main__":
    workspace = Workspace()
    workspace_controller = CtrlWorkspace(workspace)
    view_controller = CtrlView(workspace_controller)
    view_controller.view.robot.rotate_head(-45)

    # Add points of interest directly to the view_controller
    view_controller.add_point_of_interest(150, 0, EXPERIENCE_FLOOR)
    view_controller.add_point_of_interest(300, -300, EXPERIENCE_ALIGNED_ECHO)

    # Add points of interest to the memory
    # view_controller.memory.add((0, 1, 0, 0, 0, 0))

    # Update the list of points of interest from memory
    last_used_id = -1
    _interactions_list = [elem for elem in view_controller.memory.interactions if elem.id > last_used_id]
    for _interaction in _interactions_list:
        if _interaction.id > last_used_id:
            last_used_id = max(_interaction.id, last_used_id)
        _poi = view_controller.create_point_of_interest(_interaction)
        view_controller.points_of_interest.append(_poi)

    pyglet.app.run()
