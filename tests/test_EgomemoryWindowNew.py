# By Olivier GEORGEON 15 March 2022

from EgoMemoryWindowNew import EgoMemoryWindowNew
from ControllerNew import ControllerNew
from Synthesizer import Synthesizer
from MemoryV1 import MemoryV1
from Agent6 import Agent6
from HexaMemory import HexaMemory
import pyglet
from HexaView import HexaView
import json
from Agent5 import Agent5

CONTROL_MODE_MANUAL = 0
CONTROL_MODE_AUTOMATIC = 1
control_mode = CONTROL_MODE_MANUAL
print("Control mode: MANUAL")


# Testing ControllerNew by remote controlling the robot from the EgoMemoryWindowNew
if __name__ == "__main__":
    emw = EgoMemoryWindowNew()
    emw2 = EgoMemoryWindowNew()
    emw2.set_caption("North up projection")
    memory = MemoryV1()
    hexa_memory = HexaMemory(width=30, height=100, cells_radius=50)
    agent_act = Agent5()
    agent = Agent6(memory, hexa_memory)
    hexaview = HexaView()
    synthesizer = Synthesizer(memory,hexa_memory)
    controller = ControllerNew(agent, memory, view=emw, synthesizer = synthesizer, hexa_memory = hexa_memory, hexaview = hexaview)
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
                controller.command_robot(text)
            else:
                print("Waiting for previous outcome before sending new action")

    def main_loop(dt):
        """ Watch for the end of the previous interaction and choose the next """
        if controller.enact_step == 2:
            # Update the egocentric memory window
            robot_data = controller.outcome_bytes
            phenom_info, angle, translation, controller.outcome = controller.translate_robot_data(robot_data)
            controller.send_position_change_to_memory(angle,translation) #Might be an order problem between this line and the one under it, depending on
            controller.send_phenom_info_to_memory(phenom_info) # when the robot detect interaction (before or after moving)
            emw.extract_and_convert_interactions(memory)
            emw2.extract_and_convert_interactions(memory)
            emw2.azimuth = controller.azimuth
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
