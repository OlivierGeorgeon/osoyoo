import pyglet
from pyglet.gl import *
from Robot import Robot

# Zooming constants
ZOOM_IN_FACTOR = 1.2
ZOOM_OUT_FACTOR = 1/ZOOM_IN_FACTOR


class EMWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(150, 150)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        self.batch = pyglet.graphics.Batch()
        self.zoom_level = 1

        self.robot = Robot(self.batch)
        self.robot.rotate_head(20)

        # self.circle = pyglet.shapes.Circle(0, 0, 100, color=(50, 225, 30), batch=self.batch)
        # self.rect = pyglet.shapes.Rectangle(0, 0,1000, 10, color=(0, 0, 0), batch=self.batch)

    def on_draw(self):
        # Save the default model view matrix
        glLoadIdentity()
        # glPushMatrix()

        # Clear window with ClearColor
        glClear(GL_COLOR_BUFFER_BIT)

        # Set orthographic projection matrix
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Redraw
        self.batch.draw()

        # Restore default model view matrix
        # glLoadIdentity()
        # glPopMatrix()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)

    def on_mouse_scroll(self, x, y, dx, dy):
        # Get scale factor
        f = ZOOM_IN_FACTOR if dy > 0 else ZOOM_OUT_FACTOR if dy < 0 else 1
        if .2 < self.zoom_level * f < 2:
            self.zoom_level *= f


if __name__ == "__main__":
    em_window = EMWindow(400, 400, "Egocentric Memory", resizable=True)
    pyglet.app.run()
