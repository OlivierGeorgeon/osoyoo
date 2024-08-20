import pyglet
import numpy as np
from pyrr import Quaternion
from .CtrlEgocentricView import CtrlEgocentricView
from autocat.Display.ShapeDisplay import *
from ...Workspace import Workspace
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_FLOOR, EXPERIENCE_ROBOT
from ...Utils import quaternion_translation_to_matrix
from ...Proposer.Interaction import Interaction, OUTCOME_NO_FOCUS
from ...Proposer.Action import Action, ACTION_SWIPE
from ...Robot.Enaction import Enaction
from ...Robot.Outcome import Outcome

# Displaying EgocentricView with points of interest.
# Allow selecting points of interest and inserting and deleting phenomena
# py -m autocat.Display.EgocentricDisplay

workspace = Workspace('PetiteIA', '3')
ctrl_egocentric_view = CtrlEgocentricView(workspace)

# The body position in body memory
# workspace.memory.body_memory.set_head_direction_degree(-45)
# ctrl_egocentric_view.update_body_robot()

# Add experiences
pose_matrix = quaternion_translation_to_matrix(Quaternion.from_z_rotation(0.5), [150, 0, 0])
experience0 = Experience(experience_id=0, pose_matrix=pose_matrix, experience_type=EXPERIENCE_FLOOR, clock=0,
                         body_quaternion=Quaternion([0., 0., 0., 1.]))  # , direction_quaternion=Quaternion.from_z_rotation(0.5))
workspace.memory.egocentric_memory.experiences[0] = experience0

pose_matrix = quaternion_translation_to_matrix(Quaternion.from_z_rotation(0.), [300, -300, 0])
experience1 = Experience(experience_id=1, pose_matrix=pose_matrix, experience_type=EXPERIENCE_ALIGNED_ECHO, clock=0,
                         body_quaternion=Quaternion([0., 0., 0., 1.]))
workspace.memory.egocentric_memory.experiences[1] = experience1

pose_matrix = quaternion_translation_to_matrix(Quaternion.from_z_rotation(math.radians(-130)), [200, 200, 0])
experience2 = Experience(experience_id=2, pose_matrix=pose_matrix, experience_type=EXPERIENCE_ROBOT, clock=-3,
                         body_quaternion=Quaternion([0., 0., 0., 1.]), color_index=2)
workspace.memory.egocentric_memory.experiences[2] = experience2
# poi1 = controller.add_point_of_interest(150, 0, EXPERIENCE_FLOOR)
# controller.points_of_interest.append(poi1)
# poi2 = controller.add_point_of_interest(300, -300, EXPERIENCE_ALIGNED_ECHO)
# controller.points_of_interest.append(poi2)

# Create an enaction
swipe = Interaction(Action(ACTION_SWIPE, np.array([0, 300, 0], dtype=float), 0, 1.), OUTCOME_NO_FOCUS, 0)
#turn = Interaction(Action(ACTION_TURN, np.array([0, 0, 0], dtype=float), 0, 1.), OUTCOME_NO_FOCUS, 0)
workspace.memory.clock += 1
enaction = Enaction(swipe, workspace.memory.save())
enaction.outcome = Outcome({'action': ACTION_SWIPE, 'clock': 0, 'duration1': 500, 'head_angle': 0, 'yaw': 00,
                            'echo_distance': 200})
enaction.terminate()
workspace.enaction = enaction
workspace.memory.update(enaction)


ctrl_egocentric_view.update_points_of_interest()

pyglet.app.run()
