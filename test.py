from pyglet.gl import *
from pyglet import shapes
from EgoMemoryWindow import EgoMemoryWindow
from EgoMemoryWindowNew import EgoMemoryWindowNew
from PhenomenonNew import PhenomenonNew
from MemoryNew import MemoryNew
from webcolors import name_to_rgb
from pyrr import matrix44
from OsoyooCar import OsoyooCar
import math
if __name__ == "__main__":
    

    window = EgoMemoryWindowNew()
    batch = pyglet.graphics.Batch()
    robot = OsoyooCar(window.batch)
    memory = MemoryNew(window)
    rectangle = PhenomenonNew(50,50,width = 15, height = 15,color = "lime",durability = 10, decayIntensity = 1)
    triangle = PhenomenonNew(0,0,shape = 2,color = "blue",durability = 10, decayIntensity = 1)

    memory.add(rectangle)
    memory.add(triangle)
    window.set_ShapesList( memory.draw())
    #memory.empty()
    kss =  PhenomenonNew(50,50,shape = 1, width = 20, height = 15,color = "lime",durability = 10, decayIntensity = 1)
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

