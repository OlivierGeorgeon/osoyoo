# By Olivier GEORGEON 15 March 2022

import sys
import os
import time
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Osoyoo import *
from Views.EgoMemoryWindowNew import EgoMemoryWindowNew
from Controllers.ControllerNew import ControllerNew
from Model.Synthesizers.Synthesizer import Synthesizer
from Model.Memories.MemoryV1 import MemoryV1
from Agents.Agent6 import Agent6
from Model.Hexamemories.HexaMemory import HexaMemory
import pyglet
from Views.HexaView import HexaView
import json
from Agents.Agent5 import Agent5

CONTROL_MODE_MANUAL = 0
CONTROL_MODE_AUTOMATIC = 1
control_mode = CONTROL_MODE_MANUAL
print("Control mode: MANUAL")


# Testing ControllerNew by remote controlling the robot from the EgoMemoryWindowNew
# py -m tests.test_EgomemoryWindowNew <ROBOT_IP>
if __name__ == "__main__":
    ip = "192.168.1.11"
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        print("Please provide your robot's IP address")
    print("Sending to: " + ip)
    emw = EgoMemoryWindowNew()
    emw2 = EgoMemoryWindowNew()
    emw2.set_caption("North up projection")
    memory = MemoryV1()
    hexa_memory = HexaMemory(width=40, height=80, cells_radius=50)
    agent_act = Agent5()
    agent = Agent6(memory, hexa_memory)
    hexaview = HexaView()
    synthesizer = Synthesizer(memory,hexa_memory)
    controller = ControllerNew(agent, memory, ip, view=emw, synthesizer = synthesizer, hexa_memory = hexa_memory, hexaview = hexaview)
    controller.hexaview.extract_and_convert_interactions(controller.hexa_memory)

    @emw.event
    def on_text(text):
        global control_mode
        if text.upper() == "A":
            control_mode = CONTROL_MODE_AUTOMATIC
            print("Control mode: AUTOMATIC")
        elif text.upper() == "M":
            control_mode = CONTROL_MODE_MANUAL
            print("Control mode: MANUAL")

        if control_mode == CONTROL_MODE_MANUAL:
            if controller.enact_step == 0:
                controller.action_angle = emw.mouse_press_angle
                #  if text == "/" or text == "+":  # Send the angle marked by the mouse click
                #      text = json.dumps({'action': text, 'angle': emw.mouse_press_angle})
                controller.command_robot(text)
            else:
                print("Waiting for previous outcome before sending new action")

    def main_loop(dt):
        """ Watch for the end of the previous interaction and choose the next """
        if controller.enact_step == 2:
            # Update the egocentric memory window
            robot_data = controller.outcome_bytes
            phenom_info, angle, translation, controller.outcome, echo_array = controller.translate_robot_data(robot_data)
            controller.send_position_change_to_memory(angle,translation) #Might be an order problem between this line and the one under it, depending on
            controller.send_phenom_info_to_memory(phenom_info, echo_array) # when the robot detect interaction (before or after moving)
            controller.memory.tick()
            emw.extract_and_convert_interactions(memory)
            emw2.extract_and_convert_interactions(memory)
            emw2.azimuth = controller.azimuth
            emw2.robot.rotate_head(emw.robot.head_angle)
            controller.hexaview.extract_and_convert_interactions(controller.hexa_memory)
            controller.send_position_change_to_hexa_memory(angle, translation)
            controller.ask_synthetizer_to_act()
            controller.main_refresh()
            controller.enact_step = 0

        if control_mode == CONTROL_MODE_AUTOMATIC:
            if controller.enact_step == 0:
                # Retrieve the previous outcome
                outcome = 0
                json_outcome = json.loads(controller.outcome_bytes)
                if 'floor' in json_outcome:
                    outcome = json_outcome['floor']
                if 'shock' in json_outcome:
                    if json_outcome['shock'] > 0:
                        outcome = json_outcome['shock']

                # Choose the next action
                action = agent_act.action(outcome)
                controller.command_robot(['8', '1', '3'][action])

    # Schedule the main loop that updates the agent
    pyglet.clock.schedule_interval(main_loop, 0.1)

    # Run all the windows
    pyglet.app.run()
