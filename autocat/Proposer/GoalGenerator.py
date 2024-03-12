import math
from pyrr import quaternion, Quaternion, Vector3
from ..Robot.RobotDefine import TERRAIN_RADIUS
from ..Memory.PhenomenonMemory import PHENOMENON_RECOGNIZED_CONFIDENCE
from ..Memory.PhenomenonMemory.PhenomenonMemory import TER

STEP_INIT = 0
STEP_EXPLORE = 1


class GoalGenerator:
    def __init__(self, workspace):
        self.workspace = workspace
        self.explore_angle_quaternion = Quaternion.from_z_rotation(math.pi / 3)  # 2
        self.step = STEP_INIT
        self.goal_point = None

    def terrain_goal_point(self):
        """Return a new goal point in terrain centric coordinates for touring the terrain"""
        if self.step == STEP_INIT:
            self.goal_point = self.workspace.memory.phenomenon_memory.phenomena[TER].origin_direction_quaternion * \
                              Vector3([TERRAIN_RADIUS[self.workspace.arena_id]["radius"] * 1.1, 0, 0])
            self.step = STEP_EXPLORE

        # The next goal point is rotated
        self.goal_point = quaternion.apply_to_vector(self.explore_angle_quaternion, self.goal_point)

        # When the terrain has not been recognized, add the terrain radius
        if self.workspace.memory.phenomenon_memory.terrain_confidence() < PHENOMENON_RECOGNIZED_CONFIDENCE:
            return self.goal_point + self.workspace.memory.phenomenon_memory.phenomena[TER].\
                origin_direction_quaternion * Vector3([-TERRAIN_RADIUS[self.workspace.arena_id]["radius"], 0, 0])
        else:
            return self.goal_point

    def most_interesting_pool(self):
        """Return point of the pool in allocentric memory that have the highest interest value"""
        return self.workspace.memory.allocentric_memory.most_interesting_pool(self.workspace.clock)
