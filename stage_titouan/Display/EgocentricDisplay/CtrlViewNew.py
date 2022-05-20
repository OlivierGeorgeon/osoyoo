from . EgocentricView import EgocentricView
from . PointOfInterest import *
import pyglet
from pyglet.window import key


class CtrlViewNew :
    """blabla"""
    def __init__(self,ctrl_workspace):
        self.view = EgocentricView()
        self.ctrl_workspace = ctrl_workspace
        self.memory = ctrl_workspace.workspace.memory

        self.points_of_interest = []

        self.mouse_press_x = 0
        self.mouse_press_y = 0
        self.mouse_press_angle = 0
        self.last_used_id = -1
        def on_mouse_press(x, y, button, modifiers):
            """ Selecting or unselecting points of interest"""
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
                # self.add_point_of_interest(self.mouse_press_x, self.mouse_press_y, POINT_PHENOMENON,
                #                           self.ego_view.background)

        self.view.push_handlers(on_mouse_press, on_key_press)

    def add_point_of_interest(self, x, y, point_type, group=None,interaction = None):
        """ Adding a point of interest to the view """
        if group is None:
            group = self.view.foreground
        point_of_interest = PointOfInterest(x, y, self.view.batch, group, point_type,interaction = interaction)
        self.points_of_interest.append(point_of_interest)
        return point_of_interest

    def update_points_of_interest(self):
        """Retrieve all new interactions from the memory, create corresponding points of interest
        then update the shape of each POI"""
        interactions_list = [elem for elem in self.memory.interactions if elem.id > self.last_used_id]
        for interaction in interactions_list:
            if interaction.id > self.last_used_id:
                self.last_used_id = interaction.id
            poi = self.create_points_of_interest(interaction)
            self.points_of_interest.append(poi)
            

        displacement_matrix = self.ctrl_workspace.enacted_interaction['displacement_matrix'] if 'displacement_matrix' in self.ctrl_workspace.enacted_interaction else None
        for poi in self.points_of_interest:
            poi.update(displacement_matrix)

        


    def create_points_of_interest(self, interaction):
        """Create a point of interest corresponding to the interaction given as parameter"""
        dict_interactions_to_poi = {"Shock": POINT_SHOCK, "Echo": POINT_ECHO, "Trespassing": POINT_TRESPASS, 'Block': POINT_BLOCK}
        return PointOfInterest(interaction.x, interaction.y, self.view.batch, self.view.foreground,dict_interactions_to_poi[interaction.type],interaction = interaction)
        
    def main(self,dt):
        if self.ctrl_workspace.flag_for_view_refresh :
            self.update_points_of_interest()
            self.ctrl_workspace.flag_for_view_refresh = False