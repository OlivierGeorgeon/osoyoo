# .______        _______..__   __.
# |   _  \      /       ||  \ |  |
# |  |_)  |    |   (----`|   \|  |
# |   _  <      \   \    |  . `  |
# |  |_)  | .----)   |   |  |\   |
# |______/  |_______/    |__| \__|
#
#  BSN2 2021-2022
#   Aleksei Apostolou
#   Daniel Duval
#   Célien Fiorelli
#   Geordi Gampio
#   Julina Matouassiloua
#
#  ESQESE. UCLy. France

import pyglet
from OsoyooControllerBSN.Display.Controller import Controller
from OsoyooControllerBSN.Display.EgoMemoryWindow import EgoMemoryWindow
from OsoyooControllerBSN.Display.ModalWindow import ModalWindow
from OsoyooControllerBSN.Agent.Agent5 import Agent5
import json

CONTROL_MODE_MANUAL = 0
CONTROL_MODE_AUTOMATIC = 1
control_mode = CONTROL_MODE_MANUAL
print("Control mode: MANUAL")


def main():
    """ Controlling the robot with Agent5 """
    ip_ = "10.40.22.254"
    emw = EgoMemoryWindow(ip=ip_)
    controller = Controller(emw)
    agent = Agent5()

    @emw.event
    def on_text(text):
        global control_mode
        if text == "C":
            ModalWindow(controller.phenomena)
            return
        if text.upper() == "A":
            control_mode = CONTROL_MODE_AUTOMATIC
            print("Control mode: AUTOMATIC")
        elif text.upper() == "M":
            control_mode = CONTROL_MODE_MANUAL
            print("Control mode: MANUAL")

        if control_mode == CONTROL_MODE_MANUAL:
            if controller.enact_step == 0:
                if text == "/":  # Send the angle marked by the mouse click
                    text = json.dumps({'action': '/', 'angle': emw.mouse_press_angle})
                controller.enact(text)
            else:
                print("Waiting for previous outcome before sending new action")

    def watch_interaction(dt):
        """ Watch for the end of the previous interaction and choose the next """
        if controller.enact_step == 2:
            # Update the egocentric memory window
            controller.update_model()
            controller.enact_step = 0

        if control_mode == CONTROL_MODE_AUTOMATIC:
            if controller.enact_step == 0:
                # Retrieve the previous outcome
                outcome = 0
                json_outcome = json.loads(controller.outcome_bytes)
                if 'floor' in json_outcome:
                    outcome = int(json_outcome['floor'])
                if 'shock' in json_outcome:
                    if json_outcome['shock'] > 0:
                        outcome = json_outcome['shock']

                # Choose the next action
                action = agent.action(outcome)
                controller.enact(['8', '1', '3'][action])

    # Schedule the watch of the end of the previous interaction and choosing the next
    pyglet.clock.schedule_interval(watch_interaction, 0.1)

    # Run the egocentric memory window
    pyglet.app.run()


main()
