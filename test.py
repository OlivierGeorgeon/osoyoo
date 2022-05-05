from stage_titouan import *

robot_ip = "192.168.8.189"
model = Workspace()
ctrl_robot = CtrlRobot(model,robot_ip)
ctrl_view = CtrlView(model)
ctrl_hexaview = CtrlHexaview(model)
ctrl_synthe = CtrlSynthe(model)

def mains(dt):
    """blabla"""
    ctrl_robot.main(dt)
    ctrl_view.main(dt)
    ctrl_hexaview.main(dt)
    ctrl_synthe.main(dt)

pyglet.clock.schedule_interval(mains,0.1)
pyglet.app.run()