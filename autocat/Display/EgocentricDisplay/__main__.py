import pyglet
from .CtrlEgocentricView import CtrlEgocentricView
from .PointOfInterest import *
from ...Workspace import Workspace


# Displaying EgocentricView with points of interest.
# Allow selecting points of interest and inserting and deleting phenomena
# py -m autocat.Display.EgocentricDisplay
if __name__ == "__main__":
    # memory = EgocentricMemory()
    _workspace = Workspace()
    view_controller = CtrlEgocentricView(_workspace)
    view_controller.view.robot.rotate_head(-45)

    # Add points of interest directly to the view_controller
    view_controller.add_point_of_interest(150, 0, EXPERIENCE_FLOOR)
    view_controller.add_point_of_interest(300, -300, EXPERIENCE_ALIGNED_ECHO)

    # Add points of interest to the memory
    # view_controller.memory.add((0, 1, 0, 0, 0, 0))

    # Update the list of points of interest from memory
    last_used_id = -1
    _interactions_list = [elem for elem in view_controller.egocentric_memory.experiences if elem.id > last_used_id]
    for _interaction in _interactions_list:
        if _interaction.id > last_used_id:
            last_used_id = max(_interaction.id, last_used_id)
        _poi = view_controller.create_point_of_interest(_interaction)
        view_controller.points_of_interest.append(_poi)

    pyglet.app.run()
