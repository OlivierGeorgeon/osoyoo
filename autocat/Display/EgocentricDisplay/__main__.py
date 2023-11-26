import pyglet
from pyrr import Quaternion
from .CtrlEgocentricView import CtrlEgocentricView
from autocat.Display.PointOfInterest import *
from ...Workspace import Workspace
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_FLOOR, EXPERIENCE_ROBOT
from ...Utils import quaternion_translation_to_matrix


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
experience0 = Experience(pose_matrix, EXPERIENCE_FLOOR, 0, 0, experience_id=0)  # , direction_quaternion=Quaternion.from_z_rotation(0.5))
workspace.memory.egocentric_memory.experiences[0] = experience0

pose_matrix = quaternion_translation_to_matrix(Quaternion.from_z_rotation(0.), [300, -300, 0])
experience1 = Experience(pose_matrix,  EXPERIENCE_ALIGNED_ECHO, 0, 0, experience_id=1)
workspace.memory.egocentric_memory.experiences[1] = experience1

pose_matrix = quaternion_translation_to_matrix(Quaternion.from_z_rotation(math.radians(-130)), [200, 200, 0])
experience2 = Experience(pose_matrix,  EXPERIENCE_ROBOT, 0, -3, experience_id=2, color_index=1)
workspace.memory.egocentric_memory.experiences[2] = experience2
# poi1 = controller.add_point_of_interest(150, 0, EXPERIENCE_FLOOR)
# controller.points_of_interest.append(poi1)
# poi2 = controller.add_point_of_interest(300, -300, EXPERIENCE_ALIGNED_ECHO)
# controller.points_of_interest.append(poi2)

ctrl_egocentric_view.update_points_of_interest()

pyglet.app.run()
