import pyglet
from pyglet.gl import *
from pyglet import shapes
import math
from OsoyooCar import OsoyooCar
from pyrr import matrix44
from Phenomenon import Phenomenon
from MemoryNew import MemoryNew
from PhenomenonNew import PhenomenonNew
from Utils import phenomList_to_pyglet
ZOOM_IN_FACTOR = 1.2


class EgoMemoryWindowNew(pyglet.window.Window):
    def __init__(self, width=400, height=400, shapesList = None, *args, **kwargs):
        super().__init__(width, height, resizable=True, *args, **kwargs)
        self.set_caption("Egocentric Memory")
        self.set_minimum_size(150, 150)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        self.batch = pyglet.graphics.Batch()
        self.zoom_level = 1
        self.origin = shapes.Rectangle(0, 0, 60, 40, color=(150, 150, 225))
        self.origin.anchor_position = 30, 20
        self.total_displacement_matrix = matrix44.create_identity()
        self.azimuth = 0
        self.shapesList = shapesList
        # self.mouse_press_x = 0
        # self.mouse_press_y = 0
        self.mouse_press_angle = 0

    def set_ShapesList(self,s):
        self.shapesList = s

    def extract_and_convert_phenomenons(self,memory):
        phenomenons = memory.phenomenons
        self.shapesList = phenomList_to_pyglet(phenomenons,self.batch)


    def refresh(self,memory):
        self.extract_and_convert_phenomenons(memory)
        self.on_draw()


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
        shapesListo = self.shapesList
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
    memory = MemoryNew(emw,emw.batch)
    rectangle = PhenomenonNew(50,50,width = 15, height = 15,color = "lime",durability = 10, decayIntensity = 1)
    triangle = PhenomenonNew(0,0,shape = 2,color = "blue",durability = 10, decayIntensity = 1)
    memory.add(rectangle)
    memory.add(triangle)

    pyglet.app.run()
