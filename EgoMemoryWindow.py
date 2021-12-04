import pyglet
from pyglet.gl import *
from OsoyooCar import OsoyooCar
from WifiInterface import WifiInterface
import json
from Phenomenon import Phenomenon
import math
from pyglet import shapes
from RobotDefine import *
import threading

ZOOM_IN_FACTOR = 1.2


class EgoMemoryWindow(pyglet.window.Window):
    def __init__(self, width=400, height=400, *args, **kwargs):
        super().__init__(width, height, resizable=True, *args, **kwargs)
        self.set_caption("Egocentric Memory")
        self.set_minimum_size(150, 150)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        self.batch = pyglet.graphics.Batch()
        self.zoom_level = 1

        self.robot = OsoyooCar(self.batch)
        self.wifiInterface = WifiInterface()

        self.phenomena = []
        self.origin = shapes.Rectangle(0, 0, 60, 40, color=(150, 150, 225))
        self.origin.anchor_position = 30, 20

        self.environment_matrix = (GLfloat * 16)(1, 0, 0, 0,
                                                 0, 1, 0, 0,
                                                 0, 0, 1, 0,
                                                 0, 0, 0, 1)
        # pyglet.app.run()
        self.async_action = ""
        self.async_flag = 0
        self.async_outcome_string = ""

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # The transformations are stacked, and applied backward to the vertices

        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Stack the rotation of the world so the robot's front is up
        # glRotatef(90, 0.0, 0.0, 1.0)

        # Draw the robot and the phenomena
        self.batch.draw()

        # Stack the environment's displacement and draw the origin just to check
        glMultMatrixf(self.environment_matrix)
        self.origin.draw()  # Draw the origin of the robot

    def on_resize(self, width, height):
        # Always display in the whole window
        glViewport(0, 0, width, height)

    def on_mouse_scroll(self, x, y, dx, dy):
        # Inspired by https://www.py4u.net/discuss/148957
        f = ZOOM_IN_FACTOR if dy > 0 else 1/ZOOM_IN_FACTOR if dy < 0 else 1
        if .4 < self.zoom_level * f < 5:
            self.zoom_level *= f

    def on_text(self, text):
        self.async_action_trigger(text)
        # print("Send action: ", text)
        # outcome_string = self.wifiInterface.enact(text)
        # print(outcome_string)
        # self.process_outcome(text, outcome_string)

    def process_outcome(self, text, outcome_string):
        outcome = json.loads(outcome_string)
        floor_outcome = outcome['outcome']  # Agent5 uses floor_outcome

        # Presupposed displacement of the robot relative to the environment
        translation = [0, 0]
        rotation = 0
        if text == "1":
            rotation = 45
        if text == "2":
            translation[0] = -STEP_FORWARD_DISTANCE
        if text == "3":
            rotation = -45
        if text == "8":
            translation[0] = STEP_FORWARD_DISTANCE

        # Actual measured displacement if any
        if 'yaw' in outcome:
            rotation = outcome['yaw']

        # Estimate displacement due to floor change retreat
        if 'floor_outcome' in outcome:
            floor_outcome = outcome['floor_outcome']
            if floor_outcome > 0:  # Black line detected
                # Update the translation
                if text == "8":  # TODO Other actions
                    forward_duration = outcome['duration'] - 300  # Subtract retreat duration
                    translation[0] = STEP_FORWARD_DISTANCE * forward_duration/1000 - RETREAT_DISTANCE  # To be adjusted
                # Create a new floor-changed phenomenon
                obstacle = Phenomenon(150 + translation[0], 0, self.batch, 1)  # the translation will be reapplied
                self.phenomena.append(obstacle)

        # Translate and rotate all the phenomena
        for p in self.phenomena:
            p.translate(translation)
            p.rotate(rotation)

        # Update head angle
        if 'head_angle' in outcome:
            head_angle = outcome['head_angle']
            self.robot.rotate_head(head_angle)
            if text == "-" or text == "*" or text == "1" or text == "3":
                # Create a new echo phenomenon
                echo_distance = outcome['echo_distance']
                print("Echo distance %i" % echo_distance)
                x = self.robot.head_x + math.cos(math.radians(head_angle)) * echo_distance
                y = self.robot.head_y + math.sin(math.radians(head_angle)) * echo_distance
                obstacle = Phenomenon(x, y, self.batch)
                self.phenomena.append(obstacle)

        # Update the environment matrix used to keep track of the origin
        glLoadIdentity()
        glTranslatef(-translation[0], -translation[1], 0)
        glRotatef(-rotation, 0, 0, 1.0)
        glMultMatrixf(self.environment_matrix)
        glGetFloatv(GL_MODELVIEW_MATRIX, self.environment_matrix)

        return floor_outcome

    # Asynchronous interaction with the robot
    def async_action_trigger(self, text):
        def async_action(emw: EgoMemoryWindow):
            print("1. Async send " + self.async_action)
            emw.async_flag = 1
            emw.async_outcome_string = emw.wifiInterface.enact(self.async_action)
            print("2. Async receive " + emw.async_outcome_string)
            emw.async_flag = 2

        self.async_action = text
        thread = threading.Thread(target=async_action, args=[self])
        thread.start()


if __name__ == "__main__":
    em_window = EgoMemoryWindow()

    def watch_async_outcome(dt):
        if em_window.async_flag == 2:
            print("3. Async processing outcome")
            em_window.process_outcome(em_window.async_action, em_window.async_outcome_string)
            em_window.async_flag = 0

    pyglet.clock.schedule_interval(watch_async_outcome, 0.1)
    pyglet.app.run()
