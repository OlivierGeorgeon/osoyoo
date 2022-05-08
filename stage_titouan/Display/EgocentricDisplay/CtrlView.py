from . EgocentricView import EgocentricView
from . PointOfInterest import *
import pyglet
from pyglet.window import key


class CtrlView:
    """blabla"""

    def __init__(self, model):
        self.view = EgocentricView()
        self.model = model

        self.points_of_interest = []

        self.mouse_press_x = 0
        self.mouse_press_y = 0
        self.mouse_press_angle = 0

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
                            self.model.memory.interactions.remove(p.interaction)
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

    # def rotate_head(self, head_angle):
    #     self.ego_view.robot.rotate_head(head_angle)

    def displace(self, displacement_matrix):
        """ Moving all the points of interest by the displacement matrix """
        for p in self.points_of_interest:
            p.displace(displacement_matrix)

    def update_model(self, enacted_interaction):
        """ Updating the model from the latest received outcome """

        # If timeout then no egocentric view update
        if enacted_interaction['status'] == "T":
            print("No ego memory update")
            return

        # Translate and rotate all the previous points of interest
        for p in self.points_of_interest:
            p.displace(enacted_interaction['displacement_matrix'])

        # Mark the new position
        self.add_point_of_interest(0, 0, POINT_PLACE)

        # Update the robot's position
        self.view.robot.rotate_head(enacted_interaction['head_angle'])
        self.view.azimuth = enacted_interaction['azimuth']

        # Add new points of interest interactions
        dict_interactions_to_poi = {"Shock": POINT_SHOCK, "Echo": POINT_ECHO, "Trespassing": POINT_TRESPASS, 'Block': POINT_BLOCK}
        for p in enacted_interaction['points']:
            if p[0] in dict_interactions_to_poi:
                self.add_point_of_interest(p[1], p[2], dict_interactions_to_poi[p[0]])

        # Point of interest compass
        if 'compass_x' in enacted_interaction:
            self.add_point_of_interest(enacted_interaction['compass_x'],
                                       enacted_interaction['compass_y'], POINT_COMPASS)

    def extract_and_convert_interactions_to_poi(self, memory):
        """ Extracting interactions from the memory and converting them to points of interest """
        dict_interactions_to_poi = {"Shock": POINT_SHOCK, "Echo": POINT_ECHO, "Trespassing": POINT_TRESPASS, 'Block': POINT_BLOCK}
        for interaction in memory.interactions:
            if interaction.type in dict_interactions_to_poi:
                self.add_point_of_interest(interaction.x, interaction.y, dict_interactions_to_poi[interaction.type], interaction = interaction)#, self.view.group)
            else:
                print("Unknown interaction type in extract_and_convert_interactions_to_poi: ", interaction['type'])
    
    def get_focus_phenomenon(self):
        """ Returning the first selected phenomenon """
        for p in self.points_of_interest:
            if p.type == POINT_PHENOMENON and p.is_selected:
                return p
        return None

    def main(self,dt):
        if self.model.f_reset_flag :
            self.view = EgocentricView()
        if self.model.f_new_things_in_memory :
            print("LAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            self.points_of_interest = []
            self.extract_and_convert_interactions_to_poi(self.model.memory)
            #self.update_model(self.model.enacted_interaction)
            self.model.f_new_things_in_memory = False


# Displaying EgocentricView with points of interest
# py -m stage_titouan.Display.EgocentricDisplay.CtrlView
if __name__ == "__main__":

    controller = CtrlView(None)
    controller.view.robot.rotate_head(-45)

    # Add points of interest
    controller.add_point_of_interest(150, 0, POINT_TRESPASS)
    controller.add_point_of_interest(300, -300, POINT_ECHO)

    pyglet.app.run()
