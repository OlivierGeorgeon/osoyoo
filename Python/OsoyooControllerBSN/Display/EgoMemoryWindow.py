import pyglet
from pyglet.gl import *
from ..Display.OsoyooCar import OsoyooCar
from ..Wifi.WifiInterface import WifiInterface
import json
from ..Display.Phenomenon import Phenomenon
import math
from pyglet import shapes
from pyglet import clock

import threading
import time

# Zooming constants
ZOOM_IN_FACTOR = 1.2
ZOOM_OUT_FACTOR = 1 / ZOOM_IN_FACTOR


class ModalWindow(pyglet.window.Window):
    # draw a modalwindow
    # take a phenomena in parameter
    def __init__(self, phenomena):
        super(ModalWindow, self).__init__(width=100, height=100, resizable=True)

        self.label = pyglet.text.Label('Appuyer sur "O" pour confirmer la suppression', font_name='Times New Roman',
                                       font_size=36, x=200, y=160)
        self.label.anchor_position = 100, 80
        self.phenomena = phenomena

    def on_draw(self):
        # function for window drawing code in the on_draw event
        self.clear()
        self.label.draw()

    def on_text(self, text):
        # the on_text event called when this event is triggered
        # param : text
        print("Send action:", text)
        if text == "O":
            self.phenomena.clear()
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
        # glRotatef(90, 0.0, 0.0, 1.0) #mettre le Azimuth
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

    def clear_ms(self):
        # clear a spatial memory
        print("clear_ms")
        self.phenomena.clear()

    # def on_text(self, text):
        # print("Send action: ", text)
        # outcome_string = self.wifiInterface.enact({"action": text})
        # print(outcome_string)
        # outcome = json.loads(outcome_string)

        # self.windowRefresh(text, outcome)

    def windowRefresh(self, text, outcome):

        # text
        # outcome
        # head_angle: to manage the angle of the robot head
        # Update the model from the outcome
        translation = [0, 0]
        rotation = 0
        if text == "4":
            rotation = 45
        if text == "2":
            translation[0] = 180
        if text == "6":
            rotation = -45
        if text == "8":
            translation[0] = -180
        if text == "C":
            window = ModalWindow(self.phenomena)

        if 'head_angle' in outcome:
            head_angle = int(outcome['head_angle'])
            print(f"Head angle {head_angle}")
            self.robot.rotate_head(head_angle)

        if 'yaw' in outcome:
            rotation = float(outcome['yaw'])

        if 'echo_distance' in outcome and 'head_angle' in outcome:
            echo_distance = float(outcome['echo_distance'])
            print(F"Echo distance {echo_distance}")
            x = self.robot.head_x + math.cos(math.radians(head_angle)) * echo_distance
            y = self.robot.head_y + math.sin(math.radians(head_angle)) * echo_distance
            obstacle = Phenomenon(x, y, self.batch)
            self.phenomena.append(obstacle)

        # détecter la ligne noire
        if 'floor' in outcome:
            floor = int(outcome['floor'])
            print(f"Floor {floor}")

            if floor:
                line = Phenomenon(150, 0, self.batch, 1)
                self.phenomena.append(line)

        for p in self.phenomena:
            p.translate(translation)
            p.rotate(-rotation)

        glLoadIdentity()
        glTranslatef(translation[0], translation[1], 0)
        glRotatef(-rotation, 0, 0, 1.0)
        glMultMatrixf(self.environment_matrix)
        glGetFloatv(GL_MODELVIEW_MATRIX, self.environment_matrix)

    def actionLoop(self, frequence):
        # Loop in the background to regularly ask the robot for information
        def loop(obj: EgoMemoryWindow):
            while True:
                time.sleep(frequence)
                # print("Data requests")
                obj.outcome = obj.wifiInterface.enact({"action": "$"})
                # obj.windowRefresh('$', json.loads(outcome))

        thread = threading.Thread(target=loop, args=[self])
        thread.start()

    def actionLoopInterprete(self, dt):
        # Loop executed by pyglet to use the actionLoop functions
        if self.outcome != "{}":
            # print(self.outcome)
            self.windowRefresh('$', json.loads(self.outcome))
            self.outcome = "{}"

    # This condition is used to develop a module that can both be executed directly,
    # but also be imported by another module to provide its functions
    # window updates
if __name__ == "__main__":
    ip_ = "10.40.22.255"
    em_window = EgoMemoryWindow(ip=ip_)
    # em_window.actionLoop(10)
    # clock.schedule_interval(em_window.actionLoopInterprete, 5)
    pyglet.app.run()