from HexaMemory import HexaMemory
from Utils import hexaMemory_to_pyglet
from pyglet.gl import *
from pyglet import shapes
from HexaView import HexaView
import random
import time
if __name__ == '__main__':
    view = HexaView()
    hx = HexaMemory(17,20)
    # ...transform, update, create all objects that need to be rendered
    batch = view.batch
    shapeList = hexaMemory_to_pyglet(hx,batch)
    direction = 0
    while(True):
        view.refresh()
        print("Direction : ",direction)
        hx.move(direction,100)
        direction = random.randint(0,5)
        shapeList = hexaMemory_to_pyglet(hx,batch)
        time.sleep(1)
        print("RObot pos =", hx.get_robot_pos())

    

    #pyglet.app.run()