import math
import numpy
from pyrr import matrix44
import pyglet
from .CtrlPhenomenonView import CtrlPhenomenonView
from ...Workspace import Workspace
from ...Integrator.Phenomenon import Phenomenon
from ...Integrator.Affordance import Affordance
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO

# Testing the Phenomenon View
# py -m autocat.Display.PhenomenonDisplay
workspace = Workspace()
controller = CtrlPhenomenonView(workspace)

# Create a phenomenon
experience1 = Experience(200, 0, EXPERIENCE_ALIGNED_ECHO, math.pi / 4, experience_id=0)
# The position to place the phenomenon at the center of allocentric memory
# position_matrix = matrix44.create_identity()
affordance1 = Affordance(numpy.array([0, 0, 0], dtype=numpy.int16), experience1)
phenomenon = Phenomenon(affordance1)

# Add a second affordance
experience2 = Experience(200, 0, EXPERIENCE_ALIGNED_ECHO, -math.pi / 2, experience_id=0)
# phenomenon.affordances.append(Affordance(numpy.array([10, 50, 0], dtype=numpy.int16), experience2))
# phenomenon.try_and_add(Affordance(numpy.array([10, 50, 0], dtype=numpy.int16), experience2))
affordance2 = Affordance(numpy.array([10, 50, 0], dtype=numpy.int16), experience2)
phenomenon.try_and_add(affordance2)
# phenomenon.try_and_add(experience2, numpy.array([10, 50, 0], dtype=numpy.int16))

experience3 = Experience(200, -50, EXPERIENCE_ALIGNED_ECHO, -math.pi / 2, experience_id=0)
affordance3 = Affordance(numpy.array([100, 50, 0], dtype=numpy.int16), experience3)
phenomenon.try_and_add(affordance3)
# phenomenon.affordances.append(Affordance(numpy.array([100, 50, 0], dtype=numpy.int16), experience3))

experience4 = Experience(300, 0, EXPERIENCE_ALIGNED_ECHO, 3 * math.pi / 4, experience_id=0)
affordance4 = Affordance(numpy.array([100, 0, 0], dtype=numpy.int16), experience4)
phenomenon.try_and_add(affordance4)
# phenomenon.affordances.append(Affordance(numpy.array([100, 0, 0], dtype=numpy.int16), experience4))

# Test is_inside
print("Point [-1, -1] is inside: ", phenomenon.is_inside(numpy.array([-1, -1])))
print("Point [1, 1] is inside: ", phenomenon.is_inside(numpy.array([1, 1])))

# Test suppression
# phenomenon.affordances = [a for a in phenomenon.affordances if
#                           numpy.linalg.norm(a.position_point - [0, 0, 0]) > numpy.linalg.norm(80)]

# Update the phenomenon view
controller.update_points_of_interest(phenomenon)

# The robot azimuth in body_memory
workspace.memory.body_memory.set_body_direction_from_azimuth(45)
controller.update_body_robot()

# The robot position relative to the phenomenon
controller.view.robot_pos_x = -150
controller.view.robot_pos_y = -150

pyglet.app.run()
