# Testing the Phenomenon View
# py -m autocat.Display.PhenomenonDisplay

import math
import numpy as np
import pyglet
from pyrr import Quaternion, Matrix44
from .CtrlPhenomenonView import CtrlPhenomenonView
from ...Workspace import Workspace
from ...Memory.PhenomenonMemory.PhenomenonObject import PhenomenonObject
from ...Memory.PhenomenonMemory.Affordance import Affordance
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO
from ...Utils import quaternion_translation_to_matrix

workspace = Workspace("PetiteIA", "1")
controller = CtrlPhenomenonView(workspace)

# The robot position relative the phenomenon
workspace.memory.body_memory.body_quaternion = Quaternion.from_z_rotation(math.pi/4)
controller.view.update_body_display(workspace.memory.body_memory)
controller.view.robot_translate = [-150, -150, 0]
controller.view.robot_rotate = 90 - workspace.memory.body_memory.body_azimuth()

# Floor affordance
pose_matrix = quaternion_translation_to_matrix(Quaternion.from_z_rotation(0), [50, 0, 0])
experience0 = Experience(0, pose_matrix, EXPERIENCE_FLOOR, 0, workspace.memory.body_memory.body_quaternion)
affordance0 = Affordance(np.array([0, 0, 0]), EXPERIENCE_FLOOR, 0, 0, experience0.absolute_quaternion(),
                         experience0.polar_sensor_point())
phenomenon = PhenomenonObject(affordance0)

# Add a second affordance
pose_matrix = quaternion_translation_to_matrix(Quaternion.from_z_rotation(0), [200, 0, 0])
experience2 = Experience(2, pose_matrix, EXPERIENCE_ALIGNED_ECHO, 1, workspace.memory.body_memory.body_quaternion)
affordance2 = Affordance(np.array([10, 0, 0]), EXPERIENCE_ALIGNED_ECHO, 1, 0, experience2.absolute_quaternion(),
                         experience2.polar_sensor_point())
phenomenon.update(affordance2)

# The position of the experience and its direction must match
pose_matrix = quaternion_translation_to_matrix(Quaternion.from_z_rotation(-0.4), [200, -50, 0])
experience3 = Experience(3, pose_matrix, EXPERIENCE_ALIGNED_ECHO, 2, workspace.memory.body_memory.body_quaternion)
affordance3 = Affordance(np.array([100, 50, 0]), EXPERIENCE_ALIGNED_ECHO, 2, 0, experience3.absolute_quaternion(),
                         experience3.polar_sensor_point())
phenomenon.update(affordance3)

pose_matrix = Matrix44.from_translation([300, 0, 0], dtype=float)
experience4 = Experience(4, pose_matrix, EXPERIENCE_ALIGNED_ECHO, 3, workspace.memory.body_memory.body_quaternion)
affordance4 = Affordance(np.array([100, 0, 0]), EXPERIENCE_ALIGNED_ECHO, 3, 0, experience4.absolute_quaternion(),
                         experience4.polar_sensor_point().copy())
phenomenon.update(affordance4)

# Test is_inside
print("Point [-1, -1] is inside: ", phenomenon.is_inside(np.array([-1, -1])))
print("Point [10, 10] is inside: ", phenomenon.is_inside(np.array([10, 10])))

# Test suppression
# phenomenon.affordances = [a for a in phenomenon.affordances if
#                           numpy.linalg.norm(a.position_point - [0, 0, 0]) > numpy.linalg.norm(80)]

# Update the phenomenon view
workspace.memory.phenomenon_memory.phenomena[1] = phenomenon
controller.phenomenon_id = 1
controller.update_affordance_displays()


# The robot position relative to the phenomenon
# controller.view.robot_pos_x = -150
# controller.view.robot_pos_y = -150

pyglet.app.run()
