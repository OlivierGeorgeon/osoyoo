#   ____  __ __  ______   ___     __   ____  ______
#  /    ||  |  ||      | /   \   /  ] /    ||      |
# |  o  ||  |  ||      ||     | /  / |  o  ||      |
# |     ||  |  ||_|  |_||  O  |/  /  |     ||_|  |_|
# |  _  ||  :  |  |  |  |     /   \_ |  _  |  |  |  
# |  |  ||     |  |  |  |     \     ||  |  |  |  |  
# |__|__| \__,_|  |__|   \___/ \____||__|__|  |__|  
#
# Run main.py with the robot's IP address:
# py main.py "192.168.1.20"
#
#  Spring 2022
#   Titoua Knockart, Université Claude Bernard (UCBL), France
#  BSN2 2021-2022
#   Aleksei Apostolou, Daniel Duval, Célien Fiorelli, Geordi Gampio, Julina Matouassiloua
#  Teachers
#   Raphaël Cazorla, Florian Tholin, Olivier Georgeon
#  Bachelor Sciences du Numérique. ESQESE. UCLy. France

import sys
import pyglet
from autocat import Workspace, CtrlRobot, CtrlEgocentricView, CtrlAllocentricView, CtrlBodyView, CtrlPhenomenonView
from playsound import playsound

robot_ip = "192.168.8.189"
if len(sys.argv) > 1:
    robot_ip = sys.argv[1]
print("Robot IP:", robot_ip)

workspace = Workspace()
ctrl_robot = CtrlRobot(robot_ip, workspace)
ctrl_egocentric_view = CtrlEgocentricView(workspace)
ctrl_allocentric_view = CtrlAllocentricView(workspace)
ctrl_body_view = CtrlBodyView(workspace)
ctrl_phenomenon_view = CtrlPhenomenonView(workspace)
workspace.ctrl_phenomenon_view = ctrl_phenomenon_view


def update(dt):
    """The updates in the main loop"""
    workspace.main(dt)
    ctrl_robot.main(dt)
    ctrl_egocentric_view.main(dt)
    ctrl_allocentric_view.main(dt)
    ctrl_body_view.main(dt)
    ctrl_phenomenon_view.main(dt)


playsound('autocat/Assets/R5.wav', False)
pyglet.clock.schedule_interval(update, 0.1)
pyglet.app.run()
