from webcolors import name_to_rgb
from pyrr import matrix44, Quaternion
import math


INTERACTION_ECHO = 'Echo'
INTERACTION_ECHO2 = 'Echo2'
INTERACTION_BLOCK = 'Block'
INTERACTION_SHOCK = 'Shock'
INTERACTION_TRESPASSING = 'Trespassing'

class Interaction:
    """This class implements phenomenons with object-oriented programming, that can be stored in a MemoryNew object and then translated to pyglet shapes.
      
    Author: TKnockaert
    """

    def __init__(self,x,y,width = 50, height = 50, type = 'None',shape = 'Circle',color = 'green',durability = 10,decayIntensity = 1, starArgs = None, id = 0):
        """Create an object to be placed in the memory.

        Args:
        x : horizontal position on the matrix.
        y : vertical position on the matrix.
        type : type of phenomenons (i.e. Chock, Block, Echolocalisation, Line etc)
        shape : shape of the phenomenon when draw with pyglet 'Circle', 'Rectangle', 'Star'
        durability : durability of the object, when it reach zero the object should be removed from the memory.
        decayIntensity : represent how much is removed from durability at each iteraction.

        Raise:
        Author: TKnockaert
        """
        self.rotation = 0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.durability = durability
        self.actual_durability = durability
        self.decayIntensity = decayIntensity
        self.shape = shape
        self.type = type
        self.tick_number = 0
        self.color= color
        self.rgb = name_to_rgb(color)
        self.starArgs = starArgs # At the moment, represent the number of spikes of a star
        self.id = id
        self.corners = None
        self.compute_corners()


    def compute_corners(self):
        """Compute the corners of the Interaction.
        """
        self.corners = [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height),
        ]

    def decay(self):
        """Remove one decayIntensity from the durability of the object.

        Return: The new durability after decay
        """
        self.actual_durability -= 1
        return self.actual_durability

    def isAlive(self):
        """Check if the object is alive,
        
        Return: True if the object is alive, False otherwise.
        """
        return self.durability > 0
        

    def tick(self):
        """Handle everything that happens to the phenomenon when a tick is done

        Author : TKnockaert
        """
        self.tick_number += 1
        self.decay()

    def displace(self,displacement_matrix):
        """ Applying the displacement matrix to the phenomenon """
        #  Rotate and translate the position
        if displacement_matrix is None : 
            print("HAAAAAAAAAAAAA")
        if(self.x is not None and self.y is not None):
            v = matrix44.apply_to_vector(displacement_matrix, [self.x, self.y, 0])
            self.x, self.y = v[0], v[1]
        # TO CHECK : Shape should rotate automaticly, mb, I think, idk
        q = Quaternion(displacement_matrix)
        if q.axis[2] > 0:  # Rotate around z axis upwards
            self.rotation += math.degrees(q.angle)
        else:  # Rotate around z axis downward
            self.rotation += math.degrees(-q.angle)



    ################## PRE-DONE interactions ########################
    def red_line(self, x, y) :
        """Change the Interaction to match :
        Interaction(150,0,20,60,type = 'Line', shape = 'Rectangle', color= 'red', durability = 10, decayIntensity = 1)
        """        
        self.type = 'Line'
        self.shape = 'Rectangle'
        self.color = 'red'
        self.durability = 10
        self.decayIntensity = 1
        self.x = x
        self.y = y
        self.width = 20
        self.height = 60
        print("red_line , interaction : ", self)
        return self
    def green_circle(self, x, y) :
        """Change the Interaction to match :
       obstacleInter = Interaction(x,y,width = 50,type = 'obstacle', shape = 'Circle', color = 'green', durability = 10, decayIntensity = 1)
        """        
        self.type = 'obstacle'
        self.shape = 'Circle'
        self.color = 'green'
        self.durability = 10
        self.decayIntensity = 1
        self.x = x
        self.y = y
        self.width = 50
        print("green_circle , interaction : ", self)
        return self
    def yellow_star(self, x, y):
        """Change the Interaction to match :
                Interaction(110,0,20,60, type = 'shock', shape = 'Star',color = 'yellow', durability = 10, decayIntensity = 1, starArgs = 5)
        """
        self.type = 'Shock'
        self.shape = 'Star'
        self.color = 'yellow'
        self.durability = 10
        self.decayIntensity = 1
        self.x = x
        self.y = y
        self.width = 20
        self.height = 60
        print("yellow_star , interaction : ", self)
        return self

    def __str__(self):
        """Return a string representation of the Interaction."""
        return str(self.x)+","+str(self.y)