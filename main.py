# .______        _______..__   __.
# |   _  \      /       ||  \ |  |
# |  |_)  |    |   (----`|   \|  |
# |   _  <      \   \    |  . `  |
# |  |_)  | .----)   |   |  |\   |
# |______/  |_______/    |__| \__|
#
#
# Run the main program. Provide the robot's IP address:
# > py main.py "192.168.1.20"
#
#  Spring 2022
#   Titoua Knockart, Université Claude Bernard (UCBL), France
#  BSN2 2021-2022
#   Aleksei Apostolou, Daniel Duval, Célien Fiorelli, Geordi Gampio, Julina Matouassiloua
#  Teachers
#   Raphaël Cazorla, Florian Tholin, Olivier Georgeon
#
#  Bachelor Sciences du Numérique. ESQESE. UCLy. France
#

import sys
import pyglet
from stage_titouan import CtrlWorkspace, CtrlRobot, CtrlView, CtrlHexaview

robot_ip = "192.168.8.189"
if len(sys.argv) > 1:
    robot_ip = sys.argv[1]
print("Robot IP:", robot_ip)

ctrl_workspace = CtrlWorkspace()
ctrl_robot = CtrlRobot(robot_ip, ctrl_workspace)
ctrl_view = CtrlView(ctrl_workspace)
ctrl_hexaview = CtrlHexaview(ctrl_workspace)


def update(dt):
    """The updates in the main loop"""
    ctrl_workspace.main(dt)
    ctrl_robot.main(dt)
    ctrl_view.main(dt)
    ctrl_hexaview.main(dt)


pyglet.clock.schedule_interval(update, 0.1)
pyglet.app.run()
