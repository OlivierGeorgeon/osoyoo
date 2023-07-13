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
from autocat import Flock, Workspace, CtrlRobot, CtrlEgocentricView, CtrlAllocentricView, CtrlBodyView, CtrlPhenomenonView
from playsound import playsound

if len(sys.argv) < 3:  # Argument 0 is "main.py" when launched in -m mode
    print("Please provide the arena ID and the robot ID as arguments")
    exit()

# Create the flock of robots
# workspaces = {}
# ctrl_robots = {}
# ctrl_egocentric_views = {}
# for i in range(2, len(sys.argv)):
#     workspace = Workspace(sys.argv[1], sys.argv[i])
#     workspaces[sys.argv[i]] = workspace
#     ctrl_robots[sys.argv[i]] = CtrlRobot(workspace)
#     ctrl_egocentric_views[sys.argv[i]] = CtrlEgocentricView(workspace)
#     ctrl_egocentric_views[sys.argv[i]].view.set_caption("Robot " + sys.argv[i])
#
# # Create the views for the first robot
# ctrl_allocentric_view = CtrlAllocentricView(workspaces[sys.argv[2]])
# ctrl_body_view = CtrlBodyView(workspaces[sys.argv[2]])
# ctrl_phenomenon_view = CtrlPhenomenonView(workspaces[sys.argv[2]])
# workspaces[sys.argv[2]].ctrl_phenomenon_view = ctrl_phenomenon_view

flock = Flock(sys.argv)


# def update(dt):
#     """The updates in the main loop"""
#     for robot_id in workspaces.keys():
#         ctrl_robots[robot_id].main(dt)  # Check if outcome received from the robot
#         workspaces[robot_id].main(dt)
#         ctrl_robots[robot_id].main(dt)  # Check if command to send to the robot
#         ctrl_egocentric_views[robot_id].main(dt)
#     ctrl_allocentric_view.main(dt)
#     ctrl_body_view.main(dt)
#     ctrl_phenomenon_view.main(dt)


playsound('autocat/Assets/R5.wav', False)
# pyglet.clock.schedule_interval(update, 0.1)
pyglet.clock.schedule_interval(flock.main, 0.1)
pyglet.app.run()
