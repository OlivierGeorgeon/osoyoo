import numpy as np
import pytest
from petitbrain.Integrator.Calibrator import Calibrator, CALIBRATION_SPEED_WEIGHT
from petitbrain.Proposer.Action import ACTION_FORWARD


@pytest.fixture
def calibrator_fixture(workspace_fixture):
    """Instantiate a workspace for test"""
    return Calibrator(workspace_fixture)


def test_calibrate_forward_speed(calibrator_fixture):
    """Test add half of the forward prediction error to the forward speed"""
    calibrator_fixture.workspace.memory.place_memory.forward_pe = -20
    calibrator_fixture.calibrate_forward_speed()
    assert calibrator_fixture.workspace.actions[ACTION_FORWARD].translation_speed[0] == 300 - 20 / CALIBRATION_SPEED_WEIGHT

