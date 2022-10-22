import pyglet
from .CtrlEgocentricView import CtrlEgocentricView
from .PointOfInterest import *
from ...Workspace import Workspace
from ...Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_FLOOR


# Displaying EgocentricView with points of interest.
# Allow selecting points of interest and inserting and deleting phenomena
# py -m autocat.Display.EgocentricDisplay
workspace = Workspace()
controller = CtrlEgocentricView(workspace)

# The body position in body memory
workspace.memory.body_memory.set_head_direction_degree(-45)
controller.update_body_robot()

# Add experiences
experience1 = Experience(150, 0, EXPERIENCE_FLOOR, experience_id=0)
experience2 = Experience(300, -300, EXPERIENCE_ALIGNED_ECHO, experience_id=1)
controller.create_point_of_interest(experience1)
controller.create_point_of_interest(experience2)

# Update the list of points of interest from memory
# last_used_id = -1
# experiences = [elem for elem in controller.egocentric_memory.experiences if elem.id > last_used_id]
# for experience in experiences:
#     if experience.id > last_used_id:
#         last_used_id = max(experience.id, last_used_id)
#     _poi = controller.create_point_of_interest(experience)
#     controller.points_of_interest.append(_poi)

pyglet.app.run()
