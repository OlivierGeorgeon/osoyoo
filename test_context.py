import sys
from stage_titouan import *
from stage_titouan.Synthesizer.SyntheContextV2 import SyntheContextV2
from stage_titouan.Synthesizer.CtrlSyntheContext import CtrlSyntheContext
robot_ip = "192.168.8.189"
if len(sys.argv) > 1:
    robot_ip = sys.argv[1]
print("Robot IP:", robot_ip)

model = Workspace()
model.synthesizer = SyntheContextV2(model.memory,model.hexa_memory,model)
ctrl_robot = CtrlRobot(model, robot_ip)
ctrl_view = CtrlView(model)
ctrl_hexaview = CtrlHexaview(model)
ctrl_synthe = CtrlSyntheContext(model)

#model.synthesizer.mode = "automatic"
def mains(dt):
    """blabla"""
    ctrl_robot.main(dt)
    ctrl_view.main(dt)
    ctrl_hexaview.main(dt)
    ctrl_synthe.main(dt)

pyglet.clock.schedule_interval(mains,0.1)
pyglet.app.run()