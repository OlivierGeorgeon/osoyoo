import pyglet
from pyglet.gl import *
from pyrr import matrix44
from .CtrlPhenomenonView import CtrlPhenomenonView
from ...Workspace import Workspace
from ...Integrator.Phenomenon import Phenomenon
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO

# Testing the Phenomenon View
# py -m autocat.Display.PhenomenonDisplay
workspace = Workspace()
controller = CtrlPhenomenonView(workspace)

# Create a phenomenon
experience1 = Experience(300, -300, EXPERIENCE_ALIGNED_ECHO, experience_id=1)
experience2 = Experience(150, 0, EXPERIENCE_FLOOR, experience_id=0)
position_matrix = matrix44.create_identity()  # The displacement to place the phenomenon in allocentric memory
phenomenon = Phenomenon(experience1, position_matrix)
controller.update_points_of_interest(phenomenon)

# Set the azimuth in body_memory
workspace.memory.body_memory.set_body_direction_from_azimuth(45)
controller.update_body_robot()

# The position of the robot relative to the phenomenon
controller.view.robot_pos_x = -150
controller.view.robot_pos_y = -150

pyglet.app.run()
