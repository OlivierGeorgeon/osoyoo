import pyglet
from autocat import Workspace, CtrlEgocentricView, Decider

# Initialize the robot
robot = Workspace("192.168.8.242")

# Initialize the egocentric window
egocentric_window = CtrlEgocentricView(robot)

# Initialize the automatic controller
# decider = Decider(robot)


# Define the update function
def main_update(dt):
    robot.main(dt)
    # decider.main(dt)
    egocentric_window.main(dt)


# Schedule the call to the update function every 100ms
pyglet.clock.schedule_interval(main_update, 0.1)

# Launch the GUI
# Remote-control the robot with the keyboard
# Press "A" to enter automatic mode. Press "M" to return to manual mode
pyglet.app.run()
