import pyglet
from pyglet.gl import *
from pyglet import shapes
from Interaction import Interaction
from webcolors import name_to_rgb
from Utils import rotate
import math
from pyrr import matrix44
from RobotDefine import *


class MemoryNew:
    """This class play the role of a memory manager : it stocks Interaction objects,
    apply transformations to them (such as decay)
    and also as the responsibility to translate them to concrete shapes on the GUI.
    
    This aims to make both Interaction and the view modulables.

    Author: TKnockaert
    """

    def __init__(self):
        self.interactions = []
        self.current_id = 0


    def add(self,phenom_info):
        """Translate interactions information into an interaction object, and add it to the list
        Arg :
            phenom_info : (floor,shock,blocked)
        Author : TKnockaert
        """
        x = 10
        y = 10
        floor,shock,blocked, obstacle, x , y = phenom_info
        durability = 3

        if(floor):
            floorInter = Interaction(ROBOT_FRONT_X + RETREAT_DISTANCE,0,10,60,type = 'Line', shape = 'Rectangle', color= 'black', durability = durability, decayIntensity = 1, id = self.current_id)
            self.interactions.append(floorInter)
        if shock:
            shockInter = None
            if(shock == 0b01):
                shockInter = Interaction(110,-80,20,60, type = 'shock', shape = 'Star',color = 'yellow', durability = durability, decayIntensity = 1, starArgs = 5, id = self.current_id)
                #Star(x, y, outer_radius, inner_radius, num_spikes, rotation=0, color=(255, 255, 255), batch=None, group=None)
            if(shock == 0b11):
                shockInter = Interaction(110,0,20,60, type = 'shock', shape = 'Star',color = 'yellow', durability = durability, decayIntensity = 1, starArgs = 5, id = self.current_id)
            else :
                shockInter = Interaction(110,80,20,60, type = 'shock', shape = 'Star',color = 'yellow', durability = durability, decayIntensity = 1, starArgs = 5, id = self.current_id)
            self.interactions.append(shockInter)
        if blocked :
            blockInter =  Interaction(110,0,20,60, type = 'block', shape = 'Star',color = 'red', durability = durability, decayIntensity = 1, starArgs = 6, id = self.current_id)
            self.interactions.append(blockInter)

        if obstacle :
            obstacleInter = Interaction(x,y,width = 50,type = 'obstacle', shape = 'Circle', color = 'orange', durability = durability, decayIntensity = 1, id = self.current_id)
            self.interactions.append(obstacleInter)
        
        self.current_id += 1
        

    def tick(self):
        for p in self.interactions:
            p.tick()


    def empty(self):
        self.interactions.clear()

    # def actualize(self, angle, distance):
    #     self.tick()
    #     for i in range(0, len(self.interactions)):
    #         p = self.interactions[i]
    #         x, y = rotate(p.x,p.y,angle)
    #         p.x = x
    #         p.y = y
    #
    #         p.y -= distance
    #
    #     # interaction avec durability >= 0

    def move(self, rotation, translation):
        """ Compute the displacement matrix and apply it to the interactions """
        translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
        rotation_matrix = matrix44.create_from_z_rotation(math.radians(rotation))
        displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
        # Translate and rotate all the interactions
        for interaction in self.interactions:
            interaction.displace(displacement_matrix)

        
# Testing MemoryNew by displaying interactions in an EgoMemoryWindowNew
if __name__ == "__main__":

    def func_bidon(batch):
       circle = shapes.Circle(500, 150, 100, color=(50, 225, 30), batch=batch)
       return circle

    window = pyglet.window.Window(960, 540)
    batch = pyglet.graphics.Batch()

    memory = MemoryNew()
    rectangle = Interaction(50,50,width = 15, height = 15,color = "lime",durability = 10, decayIntensity = 1)
    triangle = Interaction(0,0,shape = 2,color = "blue",durability = 10, decayIntensity = 1)

    memory.add((0, 0, 1, 0, 0, 0))
    # memory.add(triangle)
    # liste = memory.draw()

    #memory.draw()
    kss = func_bidon(batch)
    circle = shapes.Circle(700, 150, 100, color=(50, 225, 30), batch=batch)
    rectangle = shapes.Rectangle(550, 150, 100, 300, color=name_to_rgb("purple"), batch = batch)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    pyglet.app.run()
