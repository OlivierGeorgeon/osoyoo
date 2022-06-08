import pyglet
from pyglet.gl import *
from pyglet import shapes
from . Interactions.Interaction import Interaction
from . Interactions.Interaction import INTERACTION_TRESPASSING, INTERACTION_ECHO, INTERACTION_ECHO2, INTERACTION_BLOCK, INTERACTION_SHOCK
from webcolors import name_to_rgb
# from Misc import rotate
import math
from pyrr import matrix44

INTERACTION_PERSISTENCE = 20

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
        #self.it = Interaction()


    def reset(self):
        self.interactions = []
        self.current_id = 0

    def add_enacted_interaction(self, enacted_interaction):  # Added by Olivier 08/05/2022
        """ Add interactions from the enacted interaction """
        for p in enacted_interaction['points']:
            interaction = Interaction(p[1], p[2], 10, 10, type=p[0], id=self.current_id)  # TODO Adjust the parameters
            self.interactions.append(interaction)
            self.current_id += 1
        
    def add(self,phenom_info):
        """Translate interactions information into an interaction object, and add it to the list
        Arg :
            phenom_info : (floor,shock,blocked)
        Author : TKnockaert
        """
        x = 10
        y = 10
        floor,shock,blocked, obstacle, x , y = phenom_info
        durability = INTERACTION_PERSISTENCE

        if(floor):
            floorInter = Interaction(30,0,10,60,type = INTERACTION_TRESPASSING, shape = 'Rectangle', color= 'black', durability = durability, decayIntensity = 1, id = self.current_id)
            self.interactions.append(floorInter)
        if shock:
            shockInter = None
            if(shock == 0b01):
                shockInter = Interaction(110,-80,20,60, type = INTERACTION_SHOCK, shape = 'Star',color = 'yellow', durability = durability, decayIntensity = 1, starArgs = 5, id = self.current_id)
                #Star(x, y, outer_radius, inner_radius, num_spikes, rotation=0, color=(255, 255, 255), batch=None, group=None)
            if(shock == 0b11):
                shockInter = Interaction(110,0,20,60, type = INTERACTION_SHOCK, shape = 'Star',color = 'yellow', durability = durability, decayIntensity = 1, starArgs = 5, id = self.current_id)
            else :
                shockInter = Interaction(110,80,20,60, type = INTERACTION_SHOCK, shape = 'Star',color = 'yellow', durability = durability, decayIntensity = 1, starArgs = 5, id = self.current_id)
            self.interactions.append(shockInter)
        if blocked :
            blockInter =  Interaction(110,0,20,60, type = INTERACTION_BLOCK, shape = 'Star',color = 'red', durability = durability, decayIntensity = 1, starArgs = 6, id = self.current_id)
            self.interactions.append(blockInter)

        if obstacle :
            obstacleInter = Interaction(x,y,width = 5,type = INTERACTION_ECHO, shape = 'Circle', color = 'orange', durability = durability, decayIntensity = 1, id = self.current_id)
            self.interactions.append(obstacleInter)
        
        self.current_id += 1
        
    def add_echo_array(self,echo_array):
        """Convert echo array given as parameter to a list of interaction objects and add it to  self.interactions"""
        durability = INTERACTION_PERSISTENCE
        for _,echo in enumerate(echo_array):
            x = echo[0]
            #print("add_echo_array, x :",x)
            y = echo[1]
            obstacleInter = Interaction(x,y,width = 15,type = INTERACTION_ECHO, shape = 'Circle', color = 'orange', durability = durability, decayIntensity = 1, id = self.current_id)
            # obstacleInter = Interaction(x,y,width = 15,type = INTERACTION_ECHO2, shape = 'Circle', color = 'orange', durability = durability, decayIntensity = 1, id = self.current_id)
            self.interactions.append(obstacleInter)
            self.current_id += 1
    def tick(self):
        for p in self.interactions:
            p.tick()


    def empty(self):
        self.interactions.clear()

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
