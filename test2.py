from HexaMemory import HexaMemory
from Utils import hexaMemory_to_pyglet
from pyglet.gl import *
from pyglet import shapes

if __name__ == '__main__':
    window = pyglet.window.Window(960, 540)
    batch = pyglet.graphics.Batch()    
    hx = HexaMemory(50,50)

    hx.grid[0][0].set_to("Blocked")
    hx.grid[2][2].set_to("Free")
    shapeList = hexaMemory_to_pyglet(hx,batch)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    pyglet.app.run()