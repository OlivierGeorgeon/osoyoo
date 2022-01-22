import pyglet
from pyglet.gl import *
from pyglet import shapes

ZOOM_IN_FACTOR = 1.2


class EgoMemoryWindow(pyglet.window.Window):
    def __init__(self, width=400, height=400, *args, **kwargs):
        super().__init__(width, height, resizable=True, *args, **kwargs)
        self.set_caption("Egocentric Memory")
        self.set_minimum_size(150, 150)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        self.batch = pyglet.graphics.Batch()
        self.zoom_level = 1

        self.origin = shapes.Rectangle(0, 0, 60, 40, color=(150, 150, 225))
        self.origin.anchor_position = 30, 20
        self.environment_matrix = (GLfloat * 16)(1, 0, 0, 0,
                                                 0, 1, 0, 0,
                                                 0, 0, 1, 0,
                                                 0, 0, 0, 1)
        self.mouse_press_x = 0
        self.mouse_press_y = 0

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

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_press_x = int((x - self.width/2)*self.zoom_level*2)
        self.mouse_press_y = int((y - self.height/2)*self.zoom_level*2)
        print(self.mouse_press_x, self.mouse_press_y)

    def on_mouse_scroll(self, x, y, dx, dy):
        # Inspired by https://www.py4u.net/discuss/148957
        f = ZOOM_IN_FACTOR if dy > 0 else 1/ZOOM_IN_FACTOR if dy < 0 else 1
        if .4 < self.zoom_level * f < 5:
            self.zoom_level *= f

    def update_environment_matrix(self, translation, rotation):
        # Update the environment matrix used to keep track of the origin
        glLoadIdentity()
        glTranslatef(-translation[0], -translation[1], 0)
        glRotatef(-rotation, 0, 0, 1.0)
        glMultMatrixf(self.environment_matrix)
        glGetFloatv(GL_MODELVIEW_MATRIX, self.environment_matrix)


# Test the Egocentric memory windows by controlling the robot from the window
if __name__ == "__main__":
    em_window = EgoMemoryWindow()
    pyglet.app.run()
