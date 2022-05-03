from  stage_titouan import *
from architecture_test.Model import Model
from architecture_test.CtrlRobot import CtrlRobot
from architecture_test.CtrlView import CtrlView
from architecture_test.CtrlHexaview import CtrlHexaview
from architecture_test.CtrlSynthe import CtrlSynthe
import pyglet

model = Model()
ctrl_robot = CtrlRobot(model,"192.168.8.189")
ctrl_view = CtrlView(model)
ctrl_hexaview = CtrlHexaview(model)
ctrl_synthe = CtrlSynthe(model)

def mains(dt):
    ctrl_robot.main(dt)
    ctrl_view.main(dt)
    ctrl_hexaview.main(dt)
    ctrl_synthe.main(dt)

pyglet.clock.schedule_interval(mains,0.1)
pyglet.app.run()