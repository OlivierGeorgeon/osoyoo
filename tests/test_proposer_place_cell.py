import math
import pytest
from petitbrain.Proposer.ProposerPlaceCell import ProposerPlaceCell #  short_body_to_angle, open_in_front
from petitbrain.Utils import quaternion_to_direction_rad


@pytest.fixture
def proposer_fixture(workspace_fixture):
    """Instantiate a workspace for test"""
    return ProposerPlaceCell(workspace_fixture)


def test_short_body_to_angle(proposer_fixture):
    """Test with any robot body direction"""
    body_dir_rad = quaternion_to_direction_rad(proposer_fixture.workspace.memory.body_memory.body_quaternion)
    bod_dir_deg = math.degrees(body_dir_rad)
    result = proposer_fixture.short_body_to_angle(body_dir_rad)
    assert(result == 0)
    result = proposer_fixture.short_body_to_angle(math.radians(bod_dir_deg - 10))
    assert(result == pytest.approx(math.radians(-10)))
    result = proposer_fixture.short_body_to_angle(math.radians(bod_dir_deg + 10))
    assert(result == pytest.approx(math.radians(10)))
    result = proposer_fixture.short_body_to_angle(math.radians(bod_dir_deg + 90))
    assert(result == pytest.approx(math.radians(90)))
    result = proposer_fixture.short_body_to_angle(math.radians(bod_dir_deg - 90))
    assert(result == pytest.approx(math.radians(-90)))
    result = proposer_fixture.short_body_to_angle(math.radians(bod_dir_deg + 180))
    assert(result == pytest.approx(math.radians(-180)))
    result = proposer_fixture.short_body_to_angle(math.radians(bod_dir_deg + 179))
    assert(result == pytest.approx(math.radians(179)))


def test_open_in_front(proposer_fixture):
    body_dir_rad = quaternion_to_direction_rad(proposer_fixture.workspace.memory.body_memory.body_quaternion)
    bod_dir_deg = math.degrees(body_dir_rad)
    result = proposer_fixture.open_in_front(body_dir_rad, math.radians(10))
    assert result
    result = proposer_fixture.open_in_front(math.radians(bod_dir_deg + 11), math.radians(10))
    assert not result
    result = proposer_fixture.open_in_front(math.radians(bod_dir_deg - 31), math.radians(30))
    assert not result
    result = proposer_fixture.open_in_front(math.radians(101), math.radians(121))
    assert result

