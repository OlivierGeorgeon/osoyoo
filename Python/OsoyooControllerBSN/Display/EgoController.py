import threading
from ..Wifi.WifiInterface import WifiInterface
from ..Display.PointOfInterest import *
from ..Display.EgocentricView import EgocentricView
import pyglet
from pyglet.window import key


class EgoController:
    def __init__(self, ego_view: EgocentricView):
        # View
        self.ego_view = ego_view
        self.points_of_interest = []

        # Model
        self.wifiInterface = WifiInterface()

        self.action = ""
        self.enact_step = 0
        self.outcome_bytes = b'{"status":"T"}'  # Default status T timeout

        self.mouse_press_x = 0
        self.mouse_press_y = 0
        self.mouse_press_angle = 0

        def on_mouse_press(x, y, button, modifiers):
            """ Selecting or unselecting points of interest"""
            self.mouse_press_x, self.mouse_press_y, self.mouse_press_angle = \
                self.ego_view.set_mouse_press_coordinate(x, y, button, modifiers)
            for p in self.points_of_interest:
                if p.is_near(self.mouse_press_x, self.mouse_press_y):
                    p.set_color("red")
                else:
                    p.set_color()

        def on_key_press(symbol, modifiers):
            """ Deleting or inserting points of interest """
            if symbol == key.DELETE:
                for p in self.points_of_interest:
                    if p.is_selected:
                        p.delete()
                        self.points_of_interest.remove(p)
            if symbol == key.INSERT:
                self.add_point_of_interest(self.mouse_press_x, self.mouse_press_y, POINT_PHENOMENON,
                                           self.ego_view.background)

        self.ego_view.push_handlers(on_mouse_press, on_key_press)

    def add_point_of_interest(self, x, y, point_type, group=None):
        """ Adding a point of interest to the view """
        if group is None:
            group = self.ego_view.foreground
        point_of_interest = PointOfInterest(x, y, self.ego_view.batch, group, point_type)
        self.points_of_interest.append(point_of_interest)
        return point_of_interest

    # def rotate_head(self, head_angle):
    #     self.ego_view.robot.rotate_head(head_angle)

    def displace(self, displacement_matrix):
        """ Moving all the points of interest by the displacement matrix """
        for p in self.points_of_interest:
            p.displace(displacement_matrix)

    def enact(self, text):
        """ Creating an asynchronous thread to send the action to the robot and to wait for outcome """
        def enact_thread():
            """ Sending the action to the robot and waiting for outcome """
            # print("Send " + self.action)
            self.outcome_bytes = self.wifiInterface.enact(self.action)
            print("Receive ", end="")
            print(self.outcome_bytes)
            self.enact_step = 2
            # self.watch_outcome()

        self.action = text
        self.enact_step = 1
        thread = threading.Thread(target=enact_thread)
        thread.start()

    def watch_outcome(self, dt):
        """ Watching for the reception of the outcome """
        if self.enact_step == 2:
            self.update_model()
            self.enact_step = 0

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
        self.ego_view.robot.rotate_head(enacted_interaction['head_angle'])
        self.ego_view.azimuth = enacted_interaction['azimuth']

        # Interacting with a phenomenon
        floor, shock, blocked, obstacle, x, y = enacted_interaction['phenom_info']

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


# Displaying EgoMemoryWindowNew with points of interest
# py -m Python.OsoyooControllerBSN.Display.EgoController
if __name__ == "__main__":
    view = EgocentricView()
    view.robot.rotate_head(-45)

    controller = EgoController(view)

    # Add points of interest
    controller.add_point_of_interest(150, 0, POINT_TRESPASS)
    controller.add_point_of_interest(300, -300, POINT_ECHO)

    pyglet.app.run()
