import pyglet
from pyglet.gl import *
from pyglet import shapes
from Interaction import *
from webcolors import name_to_rgb
from Utils import rotate
import math

from pyrr import matrix44
class MemoryNew:
    """This class play the role of a memory manager : it stocks Interaction objects,
    apply transformations to them (such as decay)
    and also as the responsibility to translate them to concrete shapes on the GUI.
    
    This aims to make both Interaction and the view modulables.

    Author: TKnockaert
    """

    def __init__(self):
        self.phenomenons = []
        self.yaw = 0


    def add(self,phenom_info):
        """Translate interactions information into an interaction object, and add it to the list
        Arg :
            phenom_info : (floor,shock,blocked)
        Author : TKnockaert
        """
        floor,shock,blocked, obstacle, x , y = phenom_info

        if(floor):
            floorInter = Interaction(150,0,20,60,type = 'Line', shape = 'Rectangle', color= 'red', durability = 10, decayIntensity = 1)
            self.phenomenons.append(floorInter)
        if shock:
            shockInter = None
            if(shock == 1):
                shockInter = Interaction(110,-80,20,60, type = 'shock', shape = 'Star',color = 'yellow', durability = 10, decayIntensity = 1, starArgs = 5)
                #Star(x, y, outer_radius, inner_radius, num_spikes, rotation=0, color=(255, 255, 255), batch=None, group=None)
            if(shock == 2):
                shockInter = Interaction(110,0,20,60, type = 'shock', shape = 'Star',color = 'yellow', durability = 10, decayIntensity = 1, starArgs = 5)
            else :
                shockInter = Interaction(110,80,20,60, type = 'shock', shape = 'Star',color = 'yellow', durability = 10, decayIntensity = 1, starArgs = 5)
            self.phenomenons.append(shockInter)
        if blocked :
            blockInter =  Interaction(110,80,20,60, type = 'block', shape = 'Star',color = 'red', durability = 10, decayIntensity = 1, starArgs = 6)
            self.phenomenons.append(blockInter)

        if obstacle :
            obstacleInter = Interaction(x,y,width = 50,type = 'obstacle', shape = 'Circle', color = 'green', durability = 10, decayIntensity = 1)
            self.phenomenons.append(obstacleInter)
        
    """
    def draw(self):
        return phenomList_to_pyglet(self.phenomenons,self.batch)
    """
        

    def tick(self):
        for p in self.phenomenons:
            p.tick()


    def empty(self):
        self.phenomenons.clear()

    def actualize(self, angle, distance):
        self.tick()
        for i in range(0,len(self.phenomenons)):
            p = self.phenomenons[i]
            x, y = rotate(p.x,p.y,angle)
            p.x = x
            p.y = y

            p.y -= distance

        # interaction avec durability >= 0

    def move(self, rotation, translation,yaw = 0):
    # The displacement matrix of this interaction
        translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
        rotation_matrix = matrix44.create_from_z_rotation(math.radians(rotation))
        displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
        self.yaw = yaw
        # Translate and rotate all the phenomena
        for p in self.phenomenons:
            p.displace(displacement_matrix)

        

if __name__ == "__main__":
    

    def func_bidon(batch):
       circle = shapes.Circle(500, 150, 100, color=(50, 225, 30), batch=batch)
       return circle

    window = pyglet.window.Window(960, 540)
    batch = pyglet.graphics.Batch()

    memory = MemoryNew(window,batch)
    rectangle = Interaction(50,50,width = 15, height = 15,color = "lime",durability = 10, decayIntensity = 1)
    triangle = Interaction(0,0,shape = 2,color = "blue",durability = 10, decayIntensity = 1)

    memory.add(rectangle)
    memory.add(triangle)
    liste = memory.draw()

    #memory.draw()
    kss = func_bidon(batch)
    circle = shapes.Circle(700, 150, 100, color=(50, 225, 30), batch=batch)
    rectangle = shapes.Rectangle(550, 150, 100, 300, color=name_to_rgb("purple"), batch = batch)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    pyglet.app.run()
