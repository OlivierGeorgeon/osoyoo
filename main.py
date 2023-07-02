#   ____  __ __  ______   ___     __   ____  ______
#  /    ||  |  ||      | /   \   /  ] /    ||      |
# |  o  ||  |  ||      ||     | /  / |  o  ||      |
# |     ||  |  ||_|  |_||  O  |/  /  |     ||_|  |_|
# |  _  ||  :  |  |  |  |     /   \_ |  _  |  |  |  
# |  |  ||     |  |  |  |     \     ||  |  |  |  |  
# |__|__| \__,_|  |__|   \___/ \____||__|__|  |__|  
#
# Run main.py with the robot's IP address:
# py -m main.py <Arena_ID> <Robot ID>
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

if len(sys.argv) < 3:  # Argument 0 is "main.py" when launched in -m mode
    print("Please provide the arena ID and the robot ID as arguments")
    exit()

workspace = Workspace(sys.argv[1], sys.argv[2])
ctrl_robot = CtrlRobot(workspace)
ctrl_egocentric_view = CtrlEgocentricView(workspace)
ctrl_allocentric_view = CtrlAllocentricView(workspace)
ctrl_body_view = CtrlBodyView(workspace)
ctrl_phenomenon_view = CtrlPhenomenonView(workspace)
workspace.ctrl_phenomenon_view = ctrl_phenomenon_view

if len(sys.argv) > 3:
    workspace2 = Workspace(sys.argv[1], sys.argv[3])
    ctrl_robot2 = CtrlRobot(workspace2)
    ctrl_egocentric_view2 = CtrlEgocentricView(workspace2)


def update(dt):
    """The updates in the main loop"""
    ctrl_robot.main(dt)  # Check if enacted interaction received from the robot
    workspace.main(dt)
    ctrl_robot.main(dt)  # Check if intended interaction to send to the robot
    ctrl_egocentric_view.main(dt)
    ctrl_allocentric_view.main(dt)
    ctrl_body_view.main(dt)
    ctrl_phenomenon_view.main(dt)
    if len(sys.argv) > 3:
        ctrl_robot2.main(dt)
        workspace2.main(dt)
        ctrl_robot2.main(dt)
        ctrl_egocentric_view2.main(dt)
        ctrl_egocentric_view2.view.set_caption("Robot " + str(sys.argv[2]))


playsound('autocat/Assets/R5.wav', False)
pyglet.clock.schedule_interval(update, 0.1)
pyglet.app.run()
