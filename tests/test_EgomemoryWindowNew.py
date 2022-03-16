# By Olivier GEORGEON 15 March 2022

from EgoMemoryWindowNew import EgoMemoryWindowNew
from ControllerNew import ControllerNew
from Synthesizer import Synthesizer
from MemoryV1 import MemoryV1
from Agent6 import Agent6
from Agent5 import Agent5
from HexaMemory import HexaMemory
import pyglet


# Testing ControllerNew by remote controlling the robot from the EgoMemoryWindowNew
if __name__ == "__main__":
    emw = EgoMemoryWindowNew()
    emw2 = EgoMemoryWindowNew()
    emw2.set_caption("Window 2")
    memory = MemoryV1()
    hexa_memory = HexaMemory(width = 40, height = 80,cells_radius = 50)
    # agent = Agent5()
    agent = Agent6(memory, hexa_memory)

    controller = ControllerNew(agent, memory, view=emw)

    @emw.event
    def on_text(text):
        """ Receiving the action from the window and calling the controller to send the action to the robot """
        if controller.enact_step == 0:
            controller.command_robot(text)
        else:
            print("Waiting for previous outcome before sending new action")

    def watch_outcome(dt):
        if controller.enact_step >= 2:
            robot_data = controller.outcome_bytes
            phenom_info, angle, translation, controller.outcome = controller.translate_robot_data(robot_data)
            controller.send_position_change_to_memory(angle,translation) #Might be an order problem between this line and the one under it, depending on
            controller.send_phenom_info_to_memory(phenom_info) # when the robot detect interaction (before or after moving)
            controller.enact_step = 0

    # Schedule the controller to watch for the outcome received from the robot
    pyglet.clock.schedule_interval(watch_outcome, 0.1)

    # Run the egocentric memory window
    pyglet.app.run()
