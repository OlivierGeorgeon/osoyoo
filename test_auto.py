import sys
from stage_titouan import *
from stage_titouan.Synthesizer.SynthesizerSemiAuto import SynthesizerSemiAuto
from stage_titouan.Display.HexaDisplay.CtrlHexaview import CtrlHexaview
from stage_titouan.Display.HexaDisplay.CtrlHexaview2 import CtrlHexaview2
from stage_titouan.Robot.CtrlRobot import CtrlRobot
from stage_titouan.CtrlWorkspace import CtrlWorkspace
from stage_titouan.Display.EgocentricDisplay.CtrlView import CtrlView
from stage_titouan import CtrlWorkspace2
from stage_titouan import Workspace
from stage_titouan import SynthesizerAuto

from stage_titouan.Robot.CtrlRobotTest import CtrlRobotTest
from stage_titouan.CtrlWorkspaceTest import CtrlWorkspaceTest
from stage_titouan.Display.HexaDisplay.CtrlHexaviewTest import CtrlHexaviewTest
from stage_titouan.Agent.AgentRotator import AgentRotator
robot_ip = "192.168.8.189"
if len(sys.argv) > 1:
    robot_ip = sys.argv[1]
print("Robot IP:", robot_ip)

workspace = Workspace(cell_radius = 40)
workspace.synthesizer = SynthesizerAuto(workspace.memory, workspace.hexa_memory)
ctrl_workspace = CtrlWorkspaceTest(workspace)
ctrl_robot = CtrlRobotTest(robot_ip,ctrl_workspace)


ctrl_view = CtrlView(ctrl_workspace)
ctrl_hexaview = CtrlHexaviewTest(ctrl_workspace)
ctrl_workspace.workspace.agent = AgentRotator(ctrl_workspace.workspace.memory,ctrl_workspace.workspace.hexa_memory)

ctrl_workspace.workspace.agent.debug_mode = True
#model.synthesizer.mode = "automatic"
def mains(dt):
    """blabla"""
    ctrl_workspace.main(dt)
    ctrl_robot.main(dt)
    ctrl_view.main(dt)
    ctrl_hexaview.main(dt)

pyglet.clock.schedule_interval(mains,0.1)
pyglet.app.run()