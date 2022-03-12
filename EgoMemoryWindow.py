import pyglet
from pyglet.gl import *
from pyglet import shapes
import math
from OsoyooCar import OsoyooCar
from pyrr import matrix44
from Phenomenon import Phenomenon

ZOOM_IN_FACTOR = 1.2


class EgoMemoryWindow(pyglet.window.Window):
    def __init__(self, width=400, height=400, *args, **kwargs):
        super().__init__(width, height, resizable=True, *args, **kwargs)
        self.set_caption("Spatial Memory")
        self.set_minimum_size(150, 150)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        self.batch = pyglet.graphics.Batch()
        self.zoom_level = 1

        self.robot = OsoyooCar(self.batch)

        self.origin = shapes.Rectangle(0, 0, 60, 40, color=(150, 150, 225))
        self.origin.anchor_position = 30, 20
        self.total_displacement_matrix = matrix44.create_identity()
        self.azimuth = 0

        # self.mouse_press_x = 0
        # self.mouse_press_y = 0
        self.mouse_press_angle = 0

    def on_draw(self):
        """ Drawing the window """
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # The transformations are stacked, and applied backward to the vertices

        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Stack the rotation of the world so the robot's front is up
        glRotatef(90 - self.azimuth, 0.0, 0.0, 1.0)

        # Draw the robot and the phenomena
        self.batch.draw()

        # Stack the environment's displacement and draw the origin just to check
        gl_displacement_vector = [y for x in self.total_displacement_matrix for y in x]
        gl_displacement_matrix = (GLfloat * 16)(*gl_displacement_vector)
        glMultMatrixf(gl_displacement_matrix)
        self.origin.draw()  # Draw the origin of the robot

    def on_resize(self, width, height):
        """ Adjusting the viewport when resizing the window """
        # Always display in the whole window
        glViewport(0, 0, width, height)

    def on_mouse_press(self, x, y, button, modifiers):
        """ Computing the position of the mouse click relative to the robot in mm and degrees """
        mouse_press_x = int((x - self.width/2)*self.zoom_level*2)
        mouse_press_y = int((y - self.height/2)*self.zoom_level*2)
        # print(self.mouse_press_x, self.mouse_press_y)
        # The angle from the horizontal axis
        self.mouse_press_angle = int(math.degrees(math.atan2(mouse_press_y, mouse_press_x)))
        # The angle from the robot's axis
        self.mouse_press_angle += self.azimuth - 90
        if self.mouse_press_angle > 180:
            self.mouse_press_angle -= 360
        print(str(self.mouse_press_angle) + "°")

    def on_mouse_scroll(self, x, y, dx, dy):
        """ Zooming the window """
        # Inspired by https://www.py4u.net/discuss/148957
        f = ZOOM_IN_FACTOR if dy > 0 else 1/ZOOM_IN_FACTOR if dy < 0 else 1
        if .4 < self.zoom_level * f < 5:
            self.zoom_level *= f

    def update_environment_matrix(self, displacement_matrix):
        """ Updating the total displacement matrix used to keep track of the origin """
        self.total_displacement_matrix = matrix44.multiply(self.total_displacement_matrix, displacement_matrix)

    def set_batch(self, batch):
        self.batch = batch
        
# Testing the egocentric memory window by moving the environment with the keyboard
if __name__ == "__main__":
    emw = EgoMemoryWindow()
    robot = OsoyooCar(emw.batch)
    phenomena = []
    obstacle = Phenomenon(0, 0, emw.batch, 1)
    phenomena.append(obstacle)


    @emw.event
    def on_text(text):
        """ Receiving the action from the window and updating the position of the environment """
        translation = [0, 0]
        rotation = 0
        if text == "8":  # Move forward
            translation[0] = 180
        if text == "2":  # Move forward
            translation[0] = -180
        if text == "1":  # Turn left
            rotation = 45
        if text == "3":  # Turn right
            rotation = -45
        # The displacement matrix
        translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
        rotation_matrix = matrix44.create_from_z_rotation(-math.radians(-rotation))
        displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
        emw.update_environment_matrix(displacement_matrix)
        # Apply the displacement to the phenomenon
        obstacle.displace(displacement_matrix)

    pyglet.app.run()
