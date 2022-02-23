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
    
    time.sleep(1)
    
    time.sleep(20)