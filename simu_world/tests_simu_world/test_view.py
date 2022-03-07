import sys
import os
import time
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from World import World
from WorldView import WorldView


if  __name__ == '__main__':
    world = World(100,100)
    view = WorldView()
    view.refresh(world)
    while True:
        #world.move_robot(0,5,0)
        #time.sleep(0.5)
        #world.move_robot(0,0,5)
        #time.sleep(0.5)
        world.move_robot(60,0,0)
        time.sleep(5)
        print("refresh grid : ")
        view.refresh(world)
        time.sleep(5)