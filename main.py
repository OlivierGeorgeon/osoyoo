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
from stage_titouan import Workspace, CtrlWorkspace, AgentCircle, CtrlView, CtrlRobot, CtrlHexaview, Synthesizer

robot_ip = "192.168.8.189"
if len(sys.argv) > 1:
    robot_ip = sys.argv[1]
print("Robot IP:", robot_ip)

workspace = Workspace(cell_radius=40)
workspace.synthesizer = Synthesizer(workspace.memory, workspace.hexa_memory)
ctrl_workspace = CtrlWorkspace(workspace)
ctrl_robot = CtrlRobot(robot_ip, ctrl_workspace)
ctrl_view = CtrlView(ctrl_workspace)
ctrl_hexaview = CtrlHexaview(ctrl_workspace)

# Select the agent
# ctrl_workspace.change_agent(AgentRotator(ctrl_workspace.workspace.memory, ctrl_workspace.workspace.hexa_memory))
ctrl_workspace.change_agent(AgentCircle())

ctrl_workspace.workspace.agent.debug_mode = True
# model.synthesizer.mode = "automatic"


def mains(dt):
    """The main loop"""
    ctrl_workspace.main(dt)
    ctrl_robot.main(dt)
    ctrl_view.main(dt)
    ctrl_hexaview.main(dt)


pyglet.clock.schedule_interval(mains, 0.1)
pyglet.app.run()
