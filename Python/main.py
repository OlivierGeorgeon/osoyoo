# .______        _______..__   __.
# |   _  \      /       ||  \ |  |
# |  |_)  |    |   (----`|   \|  |
# |   _  <      \   \    |  . `  |
# |  |_)  | .----)   |   |  |\   |
# |______/  |_______/    |__| \__|
#
#  v0.1.0 - BSN2 2021-2022
#   Aleksei Apostolou, Daniel Duval, Célien Fiorelli, Geordi Gampio, Julina Matouassiloua
#
#  Teachers
#   Raphaël Cazorla, Florian Tholin, Olivier Georgeon
#
#  Bachelor Sciences du Numérique. ESQESE. UCLy. France
#

import sys
import pyglet
from OsoyooControllerBSN.Display.EgoController import EgoController
from OsoyooControllerBSN.Display.EgocentricView import EgocentricView
from OsoyooControllerBSN.Display.ModalWindow import ModalWindow
from OsoyooControllerBSN.Agent.Agent5 import Agent5
from OsoyooControllerBSN.Wifi.RobotController import RobotController
from OsoyooControllerBSN.Wifi.RobotDefine import *

from OsoyooControllerBSN.Display.PointOfInterest import *


CONTROL_MODE_MANUAL = 0
CONTROL_MODE_AUTOMATIC = 1
control_mode = CONTROL_MODE_MANUAL


def main(ip):
    """ Controlling the robot with Agent5 """
    emw = EgocentricView()
    ego_controller = EgoController(emw)
    robot_controller = RobotController(ip)
    agent = Agent5()

    @emw.event
    def on_text(text):
        global control_mode
        if text.upper() == "C":
            ModalWindow(ego_controller.points_of_interest)
            return
        if text.upper() == "A":
            control_mode = CONTROL_MODE_AUTOMATIC
            print("Control mode: AUTOMATIC")
        elif text.upper() == "M":
            control_mode = CONTROL_MODE_MANUAL
            print("Control mode: MANUAL")

        if control_mode == CONTROL_MODE_MANUAL:
            if robot_controller.enact_step == 0:
                intended_interaction = {'action': text, 'angle': ego_controller.mouse_press_angle}
                focus = ego_controller.get_focus_phenomenon()
                if focus:
                    intended_interaction['focus_x'] = int(focus.x)
                    intended_interaction['focus_y'] = int(focus.y)
                    intended_interaction['speed'] = STEP_FORWARD_DISTANCE
                robot_controller.command_robot(intended_interaction)
            else:
                print("Waiting for previous outcome before sending new action")

    def watch_interaction(dt):
        """ Watch for the end of the previous interaction and choose the next """
        if robot_controller.enact_step == 2:
            # Update the egocentric memory window
            enacted_interaction = robot_controller.translate_robot_data()
            ego_controller.update_model(enacted_interaction)

            # Action "+" adjusts the robot's position relative to the selected phenomenon
            if robot_controller.intended_interaction['action'] == "+" and enacted_interaction['echo_distance'] < 10000 \
                    and enacted_interaction['status'] != "T":
                focus = ego_controller.get_focus_phenomenon()
                if focus:
                    floor, shock, blocked, obstacle, x, y = enacted_interaction['phenom_info']
                    translation_matrix = matrix44.create_from_translation([x - focus.x, y - focus.y, 0])
                    ego_controller.displace(translation_matrix)

            robot_controller.enact_step = 0

        if control_mode == CONTROL_MODE_AUTOMATIC:
            if robot_controller.enact_step == 0:
                # Construct the outcome expected by Agent5
                enacted_interaction = robot_controller.translate_robot_data()
                outcome = 0
                if 'floor' in enacted_interaction:
                    outcome = int(enacted_interaction['floor'])
                if 'shock' in enacted_interaction:
                    if enacted_interaction['shock'] > 0:
                        outcome = enacted_interaction['shock']

                # Choose the next action
                action = agent.action(outcome)
                intended_interaction = {'action': ['8', '1', '3'][action]}
                robot_controller.command_robot(intended_interaction)

    # Schedule the watch of the end of the previous interaction and choosing the next
    pyglet.clock.schedule_interval(watch_interaction, 0.1)

    # Run the egocentric memory window
    pyglet.app.run()


#################################################################
# Running the main demo
# Please provide the Robot's IP address as a launch argument
#################################################################
robot_ip = "192.168.4.1"
if len(sys.argv) > 1:
    robot_ip = sys.argv[1]
else:
    print("Please provide your robot's IP address")
print("EXPECTED ROBOT IP: " + robot_ip)
print("Control mode: MANUAL")
main(robot_ip)
