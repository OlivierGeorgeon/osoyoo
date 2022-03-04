import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from World import World
from WorldView import WorldView


if  __name__ == '__main__':
    world = World(300,300)
    view = WorldView()
    view.refresh(world)
    while True:
        print("ksss")
        world.move_robot(1,50,50)
        print("ksss2")
        view.refresh(world)