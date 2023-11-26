import math
import numpy
import pyglet
from pyrr import Quaternion, Matrix44
from .CtrlPhenomenonView import CtrlPhenomenonView
from ...Workspace import Workspace
from autocat.Memory.PhenomenonMemory.PhenomenonObject import PhenomenonObject
from autocat.Memory.PhenomenonMemory.Affordance import Affordance
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO

# Testing the Phenomenon View
# py -m autocat.Display.PhenomenonDisplay
workspace = Workspace("PetiteIA", "1")
controller = CtrlPhenomenonView(workspace)

pose_matrix = Matrix44.from_translation([50, 0, 0], dtype=float)
experience0 = Experience(pose_matrix, EXPERIENCE_FLOOR, math.pi / 4, 0, experience_id=0)
affordance0 = Affordance(numpy.array([0, 0, 0], dtype=numpy.int16), experience0)
phenomenon = PhenomenonObject(affordance0)

# Create a phenomenon
pose_matrix = Matrix44.from_translation([200, 0, 0], dtype=float)
experience1 = Experience(pose_matrix, EXPERIENCE_ALIGNED_ECHO, math.pi / 4, 0, experience_id=1)
affordance1 = Affordance(numpy.array([0, 0, 0], dtype=numpy.int16), experience1)
# phenomenon = Phenomenon(affordance1)

# Add a second affordance
pose_matrix = Matrix44.from_translation([200, 0, 0], dtype=float)
experience2 = Experience(pose_matrix, EXPERIENCE_ALIGNED_ECHO, -math.pi / 2, 0, experience_id=2)
affordance2 = Affordance(numpy.array([10, 50, 0], dtype=numpy.int16), experience2)
phenomenon.update(affordance2)

pose_matrix = Matrix44.from_translation([200, -50, 0], dtype=float)
experience3 = Experience(pose_matrix, EXPERIENCE_ALIGNED_ECHO, -math.pi / 2, 0, experience_id=3)
affordance3 = Affordance(numpy.array([100, 50, 0], dtype=numpy.int16), experience3)
phenomenon.update(affordance3)

pose_matrix = Matrix44.from_translation([300, 0, 0], dtype=float)
experience4 = Experience(pose_matrix, EXPERIENCE_ALIGNED_ECHO, 3 * math.pi / 4, 0, experience_id=4)
affordance4 = Affordance(numpy.array([100, 0, 0], dtype=numpy.int16), experience4)
phenomenon.update(affordance4)

# experience5 = Experience([300, 0, 0], EXPERIENCE_ALIGNED_ECHO, 3 * math.pi / 4, 0, experience_id=5)
# affordance5 = Affordance(numpy.array([60, 0, 0], dtype=numpy.int16), experience4)
# phenomenon.update(affordance5)

# Test is_inside
print("Point [-1, -1] is inside: ", phenomenon.is_inside(numpy.array([-1, -1])))
print("Point [1, 1] is inside: ", phenomenon.is_inside(numpy.array([1, 1])))

# Test suppression
# phenomenon.affordances = [a for a in phenomenon.affordances if
#                           numpy.linalg.norm(a.position_point - [0, 0, 0]) > numpy.linalg.norm(80)]

# Update the phenomenon view
controller.update_affordance_displays(phenomenon)

# The robot position relative the phenomenon
# workspace.memory.body_memory.set_body_direction_from_azimuth(45)
workspace.memory.body_memory.body_quaternion = Quaternion.from_z_rotation(math.pi/4)
controller.update_body_robot()
controller.view.robot_translate = [-150, -150, 0]
controller.view.robot_rotate = 90 - workspace.memory.body_memory.body_azimuth()

# The robot position relative to the phenomenon
# controller.view.robot_pos_x = -150
# controller.view.robot_pos_y = -150

pyglet.app.run()
