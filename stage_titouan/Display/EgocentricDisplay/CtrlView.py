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
                self.view.set_mouse_press_coordinate(x, y, button, modifiers)
            for p in self.points_of_interest:
                p.select_if_near(self.mouse_press_x, self.mouse_press_y)

        def on_key_press(symbol, modifiers):
            """ Deleting or inserting points of interest """
            if symbol == key.DELETE:
                for p in self.points_of_interest:
                    if p.is_selected:
                        p.delete()
                        self.points_of_interest.remove(p)
            if symbol == key.INSERT:
                phenomenon = PointOfInterest(self.mouse_press_x, self.mouse_press_y, self.view.batch,
                                             self.view.background, POINT_PHENOMENON)
                self.points_of_interest.append(phenomenon)
                phenomenon.is_selected = True
                phenomenon.set_color('red')
                # self.add_point_of_interest(self.mouse_press_x, self.mouse_press_y, POINT_PHENOMENON,
                #                           self.ego_view.background)

        self.view.push_handlers(on_mouse_press, on_key_press)

    def add_point_of_interest(self, x, y, point_type, group=None):
        """ Adding a point of interest to the view """
        if group is None:
            group = self.view.foreground
        point_of_interest = PointOfInterest(x, y, self.view.batch, group, point_type)
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

        # If timeout then no ego memory update
        if enacted_interaction['status'] == "T":
            print("No ego memory update")
            return

        # Translate and rotate all the phenomena
        for p in self.points_of_interest:
            p.displace(enacted_interaction['displacement_matrix'])

        # Mark the new position
        self.add_point_of_interest(0, 0, POINT_PLACE)

        # Update the robot's position
        self.view.robot.rotate_head(enacted_interaction['head_angle'])
        self.view.azimuth = enacted_interaction['azimuth']

        # Interacting with a phenomenon
        # floor, shock, blocked, obstacle, x, y = enacted_interaction['phenom_info']
        floor = enacted_interaction['floor']
        shock = enacted_interaction['shock']
        blocked = enacted_interaction['blocked']
        obstacle = enacted_interaction['obstacle'] if 'obstacle' in enacted_interaction else None
        x = enacted_interaction['x'] if 'x' in enacted_interaction else 0
        y = enacted_interaction['y'] if 'y' in enacted_interaction else 0


        # Interaction trespassing
        if floor:
            # Mark a new trespassing interaction
            self.add_point_of_interest(x, y, POINT_TRESPASS)

        # Point of interest blocked
        if blocked:
            # Create a new push interaction
            self.add_point_of_interest(x, y, POINT_PUSH)

        # Point of interest shock
        if shock:
            self.add_point_of_interest(x, y, POINT_SHOCK)

        # Point of interest echo
        if obstacle:
            self.add_point_of_interest(x, y, POINT_ECHO)

        # Point of interest compass
        self.add_point_of_interest(enacted_interaction['compass_x'], enacted_interaction['compass_y'], POINT_COMPASS)

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
            #self.view.extract_and_convert_interactions(self.model.memory)
            self.update_model(self.model.enacted_interaction)
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
