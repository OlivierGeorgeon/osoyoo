import pyglet
from pyglet.gl import *
from ..Display.OsoyooCar import OsoyooCar
from ..Wifi.WifiInterface import WifiInterface
import json
from ..Display.Phenomenon import Phenomenon
import math
from pyglet import shapes
import threading
import time

# Zooming constants
ZOOM_IN_FACTOR = 1.2
ZOOM_OUT_FACTOR = 1 / ZOOM_IN_FACTOR


class ModalWindow(pyglet.window.Window):
    # draw a modalwindow
    # take the list of phenomena in parameter
    def __init__(self, phenomena):
        super(ModalWindow, self).__init__(width=450, height=100, resizable=True)

        self.label = pyglet.text.Label('Appuyer sur "O" pour confirmer la suppression', font_name='Times New Roman',
                                       font_size=15, x=20, y=50)
        self.label.anchor_position = 0, 0
        self.phenomena = phenomena

    def on_draw(self):
        # function for window drawing code in the on_draw event
        self.clear()
        self.label.draw()

    def on_text(self, text):
        # the on_text event called when this event is triggered
        # param : text
        print("Pressed :", text)
        if text == "O":
            # self.phenomena.clear()
            for p in self.phenomena:
                p.delete()
            ModalWindow.close(self)
        elif text == "N":
            ModalWindow.close(self)


class EgoMemoryWindow(pyglet.window.Window):
    #  to draw a main window
    # set_caption: Set the window's caption, param: string(str)
    # set_minimum_size: resize window
    def __init__(self, ip="192.168.4.1", port=8888, udpTimeout=6, *args, **kwargs):
        super().__init__(400, 400, resizable=True, *args, **kwargs)
        self.ip = ip
        self.set_caption("Egocentric Memory")
        self.set_minimum_size(150, 150)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        self.batch = pyglet.graphics.Batch()  # create a batch
        self.zoom_level = 1

        # draw the robot for display in the window using the batch parameter and used OsoyooCar's file
        self.robot = OsoyooCar(self.batch)
        self.wifiInterface = WifiInterface(ip, port, udpTimeout)

        self.phenomena = []

        # self.origin = shapes.Circle(0, 0, 20, color=(150, 150, 225))
        self.origin = shapes.Rectangle(0, 0, 60, 40, color=(150, 150, 225))
        self.origin.anchor_position = 30, 20


        self.environment_matrix = (GLfloat * 16)(1, 0, 0, 0,
                                                 0, 1, 0, 0,
                                                 0, 0, 1, 0,
                                                 0, 0, 0, 1)
        self.outcome = "{}"
        self.azimuth = 0

        # glLoadIdentity()
        # glTranslatef(150, 0, 0)
        # glGetFloatv(GL_MODELVIEW_MATRIX, self.envMat)  # The only way i found to set envMat to identity

    def on_draw(self):

        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # The transformations are stacked, and applied backward to the vertices
        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Stack the rotation of the world so the robot's front is up
        glRotatef(90 - self.azimuth, 0.0, 0.0, 1.0) #mettre le Azimuth
        # glRotatef(90, 0.0, 0.0, 1.0)
        # Draw the robot and the phenomena
        self.batch.draw()

        # Stack the environment's displacement and draw the origin just to check
        glMultMatrixf(self.environment_matrix)
        # self.origin.draw()  # Draw the origin of the robot

    def on_mouse_press(self,x, y, button, modifiers):
        # pass the event to any widgets within range of the mouse
        # the on mouse press event for mouse management
        # get the size of the window
        w, h = self.get_size()

        # mathematical formula to calculate the angle between a mouse click and the center of the window
        deltaX = x - (w/2)
        deltaY = y - (h/2)
        angleInDegrees = math.atan2(deltaY, deltaX) * 180 / math.pi
        print(int(angleInDegrees))

    def on_resize(self, width, height):
        # Display in the whole window
        glViewport(0, 0, width, height)

    def on_mouse_scroll(self, x, y, dx, dy):
        # Inspired from https://www.py4u.net/discuss/148957
        # Get scale factor
        f = ZOOM_IN_FACTOR if dy > 0 else ZOOM_OUT_FACTOR if dy < 0 else 1
        if .4 < self.zoom_level * f < 5:
            self.zoom_level *= f

    def on_text(self, text):
        """ Call the modal window to ask for conformation """
        if text == "C":
            window = ModalWindow(self.phenomena)

    def actionLoop(self, frequence):
        """ Loop in the background to regularly ask the robot for information """
        def loop(obj: EgoMemoryWindow):
            while True:
                time.sleep(frequence)
                # print("Data requests")
                obj.outcome = obj.wifiInterface.enact({"action": "$"})
                # obj.windowRefresh('$', json.loads(outcome))

        thread = threading.Thread(target=loop, args=[self])
        thread.start()

    def actionLoopInterprete(self, dt):
        """ Loop executed by pyglet to use the actionLoop functions"""
        if self.outcome != "{}":
            # print(self.outcome)
            self.windowRefresh('$', json.loads(self.outcome))
            self.outcome = "{}"


# Testing the delete phenomena functionality
# python -m Python.OsoyooControllerBSN.Display.EgoMemoryWindow
if __name__ == "__main__":
    ip_ = "10.40.22.255"
    em_window = EgoMemoryWindow(ip=ip_)
    # Add a phenomenon for test
    echo = Phenomenon(150, 0, em_window.batch, 0)
    em_window.phenomena.append(echo)

    # em_window.actionLoop(10)
    # clock.schedule_interval(em_window.actionLoopInterprete, 5)
    pyglet.app.run()