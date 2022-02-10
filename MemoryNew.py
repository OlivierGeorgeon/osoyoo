import pyglet
from pyglet.gl import *
from pyglet import shapes
from PhenomenonNew import *
from webcolors import name_to_rgb
from Utils import phenomList_to_pyglet
class MemoryNew:
    """This class play the role of a memory manager : it stocks PhenomenonNew objects,
    apply transformations to them (such as decay)
    and also as the responsibility to translate them to concrete shapes on the GUI.
    
    This aims to make both phenomenonNew and the view modulables.

    Author: TKnockaert
    """

    def __init__(self,view):
        self.phenomenons = []
        self.view = view
        self.batch = view.batch

    def add(self,phenomenon):
        self.phenomenons.append(phenomenon)

    def draw(self):
        return phenomList_to_pyglet(self.phenomenons,self.batch)
        
    def tick(self):
        for p in self.phenomenons:
            p.tick()


    def empty(self):
        self.phenomenons.clear()

if __name__ == "__main__":
    

    def func_bidon(batch):
       circle = shapes.Circle(500, 150, 100, color=(50, 225, 30), batch=batch)
       return circle

    window = pyglet.window.Window(960, 540)
    batch = pyglet.graphics.Batch()

    memory = MemoryNew(window,batch)
    rectangle = PhenomenonNew(50,50,width = 15, height = 15,color = "lime",durability = 10, decayIntensity = 1)
    triangle = PhenomenonNew(0,0,shape = 2,color = "blue",durability = 10, decayIntensity = 1)

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
