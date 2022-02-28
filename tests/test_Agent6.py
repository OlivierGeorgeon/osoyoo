import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Agent6 import Agent6
from HexaMemory import HexaMemory
from HexaView import HexaView
import time

if __name__ == '__main__':
    memory = HexaMemory(20,20)
    agent = Agent6(memory = None, hexa_memory = memory)
    view = HexaView()

    outcome = None
    action = agent.action(outcome)
    view.refresh(memory)
    
    while(True):
    #loop

        # ask action from agent 
        action = agent.action(outcome)
        print("Action : ", action)
        # tell robot to execute
        distance = 0
        rotation = 0
        if(action == 0):
            distance = 100
        elif(action == 1):
            rotation = 1
        elif(action == 2):
            rotation = 2

        # controller send pos change to hexaMem
        memory.apply_movement(rotation,distance)
        # Hexaview refresh
        view.refresh(memory)
        #time.sleep(0.2)
    
    
    time.sleep(20)