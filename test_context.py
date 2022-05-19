import sys
from stage_titouan import *
from stage_titouan.Synthesizer.SyntheContextV2 import SyntheContextV2
from stage_titouan.Synthesizer.CtrlSyntheContext import CtrlSyntheContext
from stage_titouan.Display.HexaDisplay.CtrlHexaviewNew import CtrlHexaviewNew
from stage_titouan.Robot.CtrlRobotNew import CtrlRobotNew
from stage_titouan.CtrlWorkspace import CtrlWorkspace
robot_ip = "192.168.8.189"
if len(sys.argv) > 1:
    robot_ip = sys.argv[1]
print("Robot IP:", robot_ip)

workspace = Workspace()
workspace.synthesizer = SyntheContextV2(workspace.memory,workspace.hexa_memory,workspace)
ctrl_workspace = CtrlWorkspace(workspace)
ctrl_robot = CtrlRobotNew(ctrl_workspace, robot_ip)
ctrl_view = CtrlView(workspace)
ctrl_hexaview = CtrlHexaviewNew(ctrl_workspace)

#model.synthesizer.mode = "automatic"
def mains(dt):
    """blabla"""
    ctrl_workspace.main(dt)
    ctrl_robot.main(dt)
    ctrl_view.main(dt)
    ctrl_hexaview.main(dt)

pyglet.clock.schedule_interval(mains,0.1)
pyglet.app.run()