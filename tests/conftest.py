import math
import pytest
from pyrr import Quaternion
from petitbrain.Workspace import Workspace
from petitbrain.Display.PlaceCellDisplay.CtrlPlaceCellView import CtrlPlaceCellView


@pytest.fixture
def workspace_fixture():
    """Instantiate a workspace for test"""
    workspace = Workspace("PetiteIA", "1")

    # Initialize body body
    workspace.memory.body_memory.body_quaternion = Quaternion.from_z_rotation(math.pi / 6)
    workspace.memory.body_memory.head_direction_rad = math.pi / 4

    return workspace


@pytest.fixture
def ctrl_place_cell_fix(workspace_fixture):
    """instantiate a Place cell view controller"""
    controller = CtrlPlaceCellView(workspace_fixture)
    # initialize the view from the state of the workspace
    controller.main(0)
    return controller
