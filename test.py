from pyglet.gl import *
from pyglet import shapes
from EgoMemoryWindow import EgoMemoryWindow
from EgoMemoryWindowNew import EgoMemoryWindowNew
from Interaction import Interaction
from MemoryNew import MemoryNew
from webcolors import name_to_rgb
from pyrr import matrix44
from OsoyooCar import OsoyooCar
import math
if __name__ == "bbbb":
    

    window = EgoMemoryWindowNew()
    batch = pyglet.graphics.Batch()
    robot = OsoyooCar(window.batch)
    memory = MemoryNew(window)
    rectangle = Interaction(50,50,width = 15, height = 15,color = "lime",durability = 10, decayIntensity = 1)
    triangle = Interaction(0,0,shape = 2,color = "blue",durability = 10, decayIntensity = 1)

    memory.add(rectangle)
    memory.add(triangle)
    window.set_ShapesList( memory.draw())
    #memory.empty()
    kss =  Interaction(50,50,shape = 1, width = 20, height = 15,color = "lime",durability = 10, decayIntensity = 1)
    memory.add(kss)
    window.set_ShapesList( memory.draw())

    #memory.draw()
    #kss = func_bidon(batch)
    #circle = shapes.Circle(700, 150, 100, color=(50, 225, 30), batch=batch)
    #rectangle = shapes.Rectangle(550, 150, 100, 300, color=name_to_rgb("purple"), batch = batch)

    @window.event
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
        window.update_environment_matrix(displacement_matrix)
        # Apply the displacement to the phenomenon
        #obstacle.displace(displacement_matrix)

    pyglet.app.run()


if __name__ == "__main__":


    window = pyglet.window.Window(960, 540)
    batch = pyglet.graphics.Batch()    
    x0 = 200
    y0 = 200
    radius = 100

    theta = -30 +30
    theta = math.radians(theta)
    point1 = [x0 + math.cos(theta)*radius, y0 + math.sin(theta)*radius] 
    theta = 30 +30
    theta = math.radians(theta)
    point2 = [x0 + math.cos(theta)*radius, y0 + math.sin(theta)*radius] 
    theta = 90 +30
    theta = math.radians(theta)
    point3 = [x0 + math.cos(theta)*radius, y0 + math.sin(theta)*radius] 
    theta = 150 +30
    theta = math.radians(theta)
    point4 = [x0 + math.cos(theta)*radius, y0 + math.sin(theta)*radius]
    theta = 210 +30
    theta = math.radians(theta)
    point5 = [x0 + math.cos(theta)*radius, y0 + math.sin(theta)*radius]
    theta = 270 +30
    theta = math.radians(theta)
    point6 = [x0 + math.cos(theta)*radius, y0 + math.sin(theta)*radius]

    hexagon = shapes.Polygon(point1, point2, point3, point4, point5, point6,color = (255,0,0), batch = batch)

    x1 = x0 + (point2[0]-x0  ) + radius 
    y1 = 200 + ( point2[1] - y0 )

    theta = -30 +30
    theta = math.radians(theta)
    point1 = [x1 + math.cos(theta)*radius, y1 + math.sin(theta)*radius] 
    theta = 30 +30
    theta = math.radians(theta)
    point2 = [x1 + math.cos(theta)*radius , y1 + math.sin(theta)*radius] 
    theta = 90 +30
    theta = math.radians(theta)
    point3 = [x1 + math.cos(theta)*radius , y1 + math.sin(theta)*radius] 
    theta = 150 +30
    theta = math.radians(theta)
    point4 = [x1 + math.cos(theta)*radius, y1 + math.sin(theta)*radius]
    theta = 210 +30
    theta = math.radians(theta)
    point5 = [x1 + math.cos(theta)*radius, y1 + math.sin(theta)*radius]
    theta = 270 +30
    theta = math.radians(theta)
    point6 = [x1 + math.cos(theta)*radius, y1 + math.sin(theta)*radius]

    hexagon2 = shapes.Polygon(point1, point2, point3, point4, point5, point6,color = (0,255,0), batch = batch)

    print( math.cos(math.radians(60)) - math.cos(math.radians(120)))

    hauteur = math.sqrt( (2*radius)**2 -radius**2 )
    print(hauteur)

    x2 = x0 + 3* radius 
    y2 = y0 + hauteur

    theta = -30 +30
    theta = math.radians(theta)
    point1 = [x2 + math.cos(theta)*radius, y2 + math.sin(theta)*radius] 
    theta = 30 +30
    theta = math.radians(theta)
    point2 = [x2 + math.cos(theta)*radius , y2 + math.sin(theta)*radius] 
    theta = 90 +30
    theta = math.radians(theta)
    point3 = [x2 + math.cos(theta)*radius , y2 + math.sin(theta)*radius] 
    theta = 150 +30
    theta = math.radians(theta)
    point4 = [x2 + math.cos(theta)*radius, y2 + math.sin(theta)*radius]
    theta = 210 +30
    theta = math.radians(theta)
    point5 = [x2 + math.cos(theta)*radius, y2 + math.sin(theta)*radius]
    theta = 270 +30
    theta = math.radians(theta)
    point6 = [x2 + math.cos(theta)*radius, y2 + math.sin(theta)*radius]

    hexagon3 = shapes.Polygon(point1, point2, point3, point4, point5, point6,color = (0,0,255), batch = batch)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    pyglet.app.run()