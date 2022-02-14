from webcolors import rgb_to_name
from webcolors import name_to_rgb
class Interaction:
    """This class implements phenomenons with object-oriented programming, that can be stored in a MemoryNew object and then translated to pyglet shapes.
      
    Author: TKnockaert
    """

    def __init__(self,x,y,width = 50, height = 50, type = 'None',shape = 0,color = 'green',durability = 10,decayIntensity = 1):
        """Create an object to be placed in the memory.

        Args:
        x : horizontal position on the matrix.
        y : vertical position on the matrix.
        type : type of phenomenons (i.e. Chock, Block, Echolocalisation, Line etc)
        shape : shape of the phenomenon when draw with pyglet 0 = Circle, 1 = Red Dash, 2 = Triangle
        durability : durability of the object, when it reach zero the object should be removed from the memory.
        decayIntensity : represent how much is removed from durability at each iteraction.

        Raise:
        Author: TKnockaert
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.durability = durability
        self.decayIntensity = decayIntensity
        self.shape = shape
        self.type = type
        self.tick_number = 0
        self.color= color
        self.rgb = name_to_rgb(color)
        print(self.rgb)

    def decay(self):
        """Remove one decayIntensity from the durability of the object.

        Return: The new durability after decay
        """
        self.durability -= self.decayIntensity
        return self.durability

    def isAlive(self):
        """Check if the object is alive,
        
        Return: True if the object is alive, False otherwise.
        """
        return self.durability > 0
        

    def tick(self):
        """Handle everything that happens to the phenomenon when a tick is done

        Author : TKnockaert
        """
        self.tick += 1
        self.decay()