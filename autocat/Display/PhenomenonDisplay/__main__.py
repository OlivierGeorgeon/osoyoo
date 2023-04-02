import math
import numpy
import pyglet
from .CtrlPhenomenonView import CtrlPhenomenonView
from ...Workspace import Workspace
from ...Integrator.PhenomenonObject import PhenomenonObject
from ...Integrator.Affordance import Affordance
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO

# Testing the Phenomenon View
# py -m autocat.Display.PhenomenonDisplay
workspace = Workspace()
controller = CtrlPhenomenonView(workspace)

experience0 = Experience(50, 0, EXPERIENCE_FLOOR, math.pi / 4, 0, experience_id=0)
affordance0 = Affordance(numpy.array([0, 0, 0], dtype=numpy.int16), experience0)
phenomenon = PhenomenonObject(affordance0)

# Create a phenomenon
experience1 = Experience(200, 0, EXPERIENCE_ALIGNED_ECHO, math.pi / 4, 0, experience_id=1)
affordance1 = Affordance(numpy.array([0, 0, 0], dtype=numpy.int16), experience1)
# phenomenon = Phenomenon(affordance1)

# Add a second affordance
experience2 = Experience(200, 0, EXPERIENCE_ALIGNED_ECHO, -math.pi / 2, 0, experience_id=2)
affordance2 = Affordance(numpy.array([10, 50, 0], dtype=numpy.int16), experience2)
phenomenon.update(affordance2)

experience3 = Experience(200, -50, EXPERIENCE_ALIGNED_ECHO, -math.pi / 2, 0, experience_id=3)
affordance3 = Affordance(numpy.array([100, 50, 0], dtype=numpy.int16), experience3)
phenomenon.update(affordance3)

experience4 = Experience(300, 0, EXPERIENCE_ALIGNED_ECHO, 3 * math.pi / 4, 0, experience_id=4)
affordance4 = Affordance(numpy.array([100, 0, 0], dtype=numpy.int16), experience4)
phenomenon.update(affordance4)

experience5 = Experience(300, 0, EXPERIENCE_ALIGNED_ECHO, 3 * math.pi / 4, 0, experience_id=5)
affordance5 = Affordance(numpy.array([60, 0, 0], dtype=numpy.int16), experience4)
phenomenon.update(affordance5)

# Test is_inside
print("Point [-1, -1] is inside: ", phenomenon.is_inside(numpy.array([-1, -1])))
print("Point [1, 1] is inside: ", phenomenon.is_inside(numpy.array([1, 1])))

# Test suppression
# phenomenon.affordances = [a for a in phenomenon.affordances if
#                           numpy.linalg.norm(a.position_point - [0, 0, 0]) > numpy.linalg.norm(80)]

# Update the phenomenon view
controller.update_points_of_interest(phenomenon)

# The robot position relative the phenomenon
workspace.memory.body_memory.set_body_direction_from_azimuth(45)
controller.update_body_robot()
controller.view.robot_translate = [-150, -150, 0]
controller.view.robot_rotate = 90 - workspace.memory.body_memory.body_azimuth()

# The robot position relative to the phenomenon
# controller.view.robot_pos_x = -150
# controller.view.robot_pos_y = -150

pyglet.app.run()
