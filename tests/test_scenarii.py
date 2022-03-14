import sys
import os
import time
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Synthesizer import Synthesizer
from Interaction import Interaction
from MemoryV1 import MemoryV1
from HexaMemory import HexaMemory
from HexaView import HexaView
from EgoMemoryWindowNew import EgoMemoryWindowNew
from ControllerNew import ControllerNew
from Agent6 import Agent6
if __name__ == '__main__':
    memory = MemoryV1()
    hexaMemory = HexaMemory(20,100,cells_radius = 20)
    agent = Agent6(memory,hexaMemory)
    synthesizer = Synthesizer(memory, hexaMemory)

    hexaview = HexaView()
    controller  = ControllerNew(agent,memory,synthesizer = synthesizer,
                 hexa_memory = hexaMemory, hexaview = hexaview)


# COPY OF LOOP function 
    for i in range(10) :
        controller.enact_step = 0
        controller.action = controller.ask_agent_for_action(controller.outcome) # agent -> decider
        action_debug = controller.action
        if(i % 2 == 0):
            controller.action = 0
        else :
            controller.action = 1
        robot_action = controller.translate_agent_action_to_robot_command(controller.action)
        print("<CONTROLLER> action choisie par le robot = ", controller.action)
        controller.command_robot(robot_action)
        while(controller.enact_step < 2):   # refresh la vue tant que pas de reponses de command_robot 
            if controller.view is not None:
                controller.view.refresh(controller.memory) # TODO: camerde
            if controller.hexa_memory is not None :
                controller.hexaview.refresh(controller.hexa_memory)  # TODO: camerde
        controller.enact_step = 0
        robot_data = controller.outcome_bytes
        phenom_info, angle, translation, controller.outcome = controller.translate_robot_data(robot_data)
        angle = -angle
        print(" \n \n TRANSLATION : ", translation[0], ",", translation[1], "\n\n")
        #translation = translation[1], translation[0]
        time.sleep(1)
        controller.send_position_change_to_memory(angle,translation) #Might be an order problem between this line and the one under it, depending on
        controller.send_phenom_info_to_memory(phenom_info) # when the robot detect interaction (before or after moving)
        user_interaction = None
        if controller.view is not None:
            user_interaction = controller.ask_view_to_refresh_and_get_last_interaction_from_user(controller.memory)
        controller.memory.tick()

        if controller.hexa_memory is not None :
                controller.send_position_change_to_hexa_memory(angle,translation)
        if controller.synthesizer is not None : 
            controller.ask_synthetizer_to_act()
        if controller.hexaview is not None :
            ""
            controller.ask_hexaview_to_refresh(controller.hexa_memory)
        time.sleep(2)

    time.sleep(100)