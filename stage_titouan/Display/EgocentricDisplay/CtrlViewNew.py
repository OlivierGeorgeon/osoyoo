from . EgocentricView import EgocentricView
from . PointOfInterest import *
import pyglet
from pyglet.window import key
from ... Workspace import Workspace
from ... CtrlWorkspace import CtrlWorkspace


class CtrlViewNew:
    """blabla"""
    def __init__(self, ctrl_workspace):
        self.view = EgocentricView()
        self.ctrl_workspace = ctrl_workspace
        self.memory = ctrl_workspace.workspace.memory
        self.synthesizer = ctrl_workspace.synthesizer
        self.points_of_interest = []

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
                                             self.view.background, POINT_PHENOMENON)
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

        interactions_list = [elem for elem in self.memory.interactions if elem.id > self.last_used_id]
        for interaction in interactions_list:
            if interaction.id > self.last_used_id:
                self.last_used_id = interaction.id
            poi = self.create_points_of_interest(interaction)
            self.points_of_interest.append(poi)

        real_echos_to_display = self.synthesizer.last_real_echos
        # TODO: create pointe of interest from real_echos_to_display
        for real_echo in real_echos_to_display:
            ""
            poi = self.create_pointe_of_interest_from_real_echo(real_echo)
            self.points_of_interest.append(poi)
        self.synthesizer.last_real_echos = []


        displacement_matrix = self.ctrl_workspace.enacted_interaction['displacement_matrix'] if 'displacement_matrix' in self.ctrl_workspace.enacted_interaction else None
        for poi in self.points_of_interest:
            if poi.type != 6:  # Do not displace the compass points
                poi.update(displacement_matrix)

        # Mark the new position
        self.add_point_of_interest(0, 0, POINT_PLACE)

        # Update the robot's position
        self.view.robot.rotate_head(self.ctrl_workspace.enacted_interaction['head_angle'])
        self.view.azimuth = self.ctrl_workspace.enacted_interaction['azimuth']

        # Point of interest compass
        if 'compass_x' in self.ctrl_workspace.enacted_interaction:
            self.add_point_of_interest(self.ctrl_workspace.enacted_interaction['compass_x'],
                                       self.ctrl_workspace.enacted_interaction['compass_y'], POINT_COMPASS)

    def create_points_of_interest(self, interaction):
        """Create a point of interest corresponding to the interaction given as parameter"""
        dict_interactions_to_poi = {"Shock": POINT_SHOCK, "Echo": POINT_ECHO, "Echo2": POINT_TINY_ECHO,
                                    "Trespassing": POINT_TRESPASS, 'Block': POINT_BLOCK}
        return PointOfInterest(interaction.x, interaction.y, self.view.batch, self.view.foreground,
                               dict_interactions_to_poi[interaction.type], interaction=interaction)

    def create_pointe_of_interest_from_real_echo(self,real_echo):
        """Create a point of interest corresponding to the real echo given as parameter"""
        interaction = real_echo
        return PointOfInterest(interaction.x, interaction.y, self.view.batch, self.view.foreground,
                               POINT_ECHO, interaction=interaction)
    def get_focus_phenomenon(self):
        """ Returning the first selected phenomenon """
        for p in self.points_of_interest:
            if p.type == POINT_PHENOMENON:  # and p.is_selected:
                return p
        return None

    def main(self, dt):
        """Blabla"""
        if self.ctrl_workspace.flag_for_view_refresh:
            self.points_of_interest = []
            self.update_points_of_interest()

            # Add the focus
            p = self.get_focus_phenomenon()
            if self.ctrl_workspace.agent.focus:
                if p is None:
                    self.add_point_of_interest(self.ctrl_workspace.agent.echo_xy[0],
                                               self.ctrl_workspace.agent.echo_xy[1], POINT_PHENOMENON)
            else:
                if p is not None:
                    p.delete()
                    self.points_of_interest.remove(p)

            if self.synthesizer is not None and len(self.synthesizer.last_real_echos) > 0:
                ""



                last_real_echos = []

            self.ctrl_workspace.flag_for_view_refresh = False


# Displaying EgocentricView with points of interest
# python3 -m stage_titouan.Display.EgocentricDisplay.CtrlViewNew
if __name__ == "__main__":
    workspace = Workspace()
    ctrl_workspace = CtrlWorkspace(workspace)
    ctrl_view = CtrlViewNew(ctrl_workspace)
    ctrl_view.view.robot.rotate_head(-45)

    # Add points of interest
    ctrl_view.add_point_of_interest(0, 0, POINT_PLACE)
    ctrl_view.add_point_of_interest(200, -200, POINT_COMPASS)

    # Add an interaction
    ctrl_workspace.enacted_interaction = {'status': '0', 'floor': 0, 'head_angle': 0, 'echo_distance': 221, 'ed-20': 249, 'ed-10': 247, 'ed0': 222, 'ed10': 230, 'ed20': 235, 'ed30': 874, 'ed50': 767, 'ed60': 640, 'ed70': 527, 'ed80': 467, 'ed90': 532, 'yaw': 0, 'compass_x': 76, 'compass_y': 223, 'azimuth': 251, 'duration1': 2862, 'duration': 3511, 'points': [('Echo', 301, 0)], 'echo_xy': [301, 0], 'translation': [0, 0]}
    ctrl_workspace.send_phenom_info_to_memory()
    ctrl_view.update_points_of_interest()

    pyglet.app.run()
