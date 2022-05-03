from  stage_titouan import *
from Model import Model
from CtrlRobot import CtrlRobot
from CtrlView import CtrlView
from CtrlHexaview import CtrlHexaview
from CtrlSynthe import CtrlSynthe
import pyglet

model = Model()
ctrl_robot = CtrlRobot(model)
ctrl_view = CtrlView(model)
ctrl_hexaview = CtrlHexaview(model)
ctrl_synthe = CtrlSynthe(model)

def mains():
    ctrl_robot.main()
    ctrl_view.main()
    ctrl_hexaview.main()
    ctrl_synthe.main()

pyglet.clock.schedule_interval(mains,0.1)
pyglet.app.run()