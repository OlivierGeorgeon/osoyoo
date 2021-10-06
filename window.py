import pyglet
import pyglet.window.key
from pyglet.gl import *
from pyglet import shapes

width = 1000
height = 500

window = pyglet.window.Window(width, height, "INITPROJECT", resizable=True)
batch = pyglet.graphics.Batch()

class Robot():
    def __init__(self, batch,  x, y):
        self.batch = batch
        self.x = x
        self.y = y
        self.robot()

    def resize(self, width, height):
        self.x = width/2
        self.y = height/2
        self.robot()

    def robot(self):
        height = 220
        width = 130
        self.corpsrobot = shapes.Rectangle(x=self.x, y=self.y, width=width,height=height, color=(255, 255, 255), batch=self.batch)
        self.corpsrobot.anchor_position = (65, 110)
        self.FR = shapes.Circle(x=self.x + width / 2,  y=self.y + height/2, radius=30, color=(255,255,255), batch=self.batch)
        self.RL = shapes.Circle(x=self.x - width / 2, y=self.y - height / 2, radius=30, color=(255, 255, 255),batch=self.batch)
        self.FL = shapes.Circle(x=self.x - width / 2, y=self.y + height / 2, radius=30, color=(255, 255, 255),batch=self.batch)
        self.RR = shapes.Circle(x=self.x + width / 2, y=self.y - height / 2, radius=30, color=(255, 255, 255),batch=self.batch)


bot = Robot(batch, 500, 250)



@window.event
def on_draw():
    window.clear()
    batch.draw()

@window.event
def on_resize(width, height):
    bot.resize(width, height)

pyglet.app.run()












