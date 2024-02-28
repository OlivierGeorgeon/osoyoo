import math
import numpy as np
import time
import matplotlib.path as mpath
from ..Decider.Action import ACTION_FORWARD, ACTION_SWIPE, ACTION_RIGHTWARD, ACTION_SCAN
from ..Memory.PhenomenonMemory import PHENOMENON_RECOGNIZED_CONFIDENCE
from ..Memory.AllocentricMemory.Hexagonal_geometry import point_to_cell
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_FLOOR
from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X, ROBOT_SETTINGS, ROBOT_OUTSIDE_Y
from ..Robot.Outcome import Outcome
from ..Memory.BodyMemory import point_to_echo_direction_distance
from ..Utils import assert_almost_equal_angles
from .Trajectory import Trajectory
from ..Integrator.OutcomeCode import outcome_code

RETREAT_YAW = 45


def generate_prediction(command, memory):
    """Apply the command to memory. Return the predicted outcome."""

    # By default, predict the intended duration1, yaw, and floor: 0.
    outcome_dict = {"clock": command.clock, "action": command.action.action_code, "duration1": command.duration,
                    "head_angle": memory.body_memory.head_direction_degree(), "echo_distance": 10000,
                    "yaw": command.yaw, "floor": 0}

    # If terrain is recognized, adjust the floor, duration1, and yaw outcome
    if memory.phenomenon_memory.terrain_confidence() >= PHENOMENON_RECOGNIZED_CONFIDENCE:
        # The shape of the terrain in egocentric coordinates
        # start_time = time.time()
        ego_shape = np.apply_along_axis(memory.terrain_centric_to_egocentric, 1,
                                        memory.phenomenon_memory.terrain().shape)
        # print("compute ego shape:", (time.time() - start_time) * 1000, "milliseconds")
        if command.action.action_code == ACTION_FORWARD:
            # Loop over the points where the y coordinate changes sign
            for i in np.where(np.diff(np.sign(ego_shape[:, 1])))[0]:
                # find the x coordinate of the line intersection. Tentatively set floor and yaw
                if abs(ego_shape[i + 1][0] - ego_shape[i][0]) < 5:
                    outcome_dict["floor"] = 3
                    outcome_dict["yaw"] = 0
                    x = ego_shape[i][0]
                else:
                    slope = (ego_shape[i + 1][1] - ego_shape[i][1]) / (ego_shape[i + 1][0] - ego_shape[i][0])
                    x = ego_shape[i][0] - ego_shape[i][1] / slope
                    if ego_shape[i][0] > ego_shape[i + 1][0]:
                        outcome_dict["floor"] = 1
                        outcome_dict["yaw"] = -RETREAT_YAW
                    else:
                        outcome_dict["floor"] = 2
                        outcome_dict["yaw"] = RETREAT_YAW
                # If the line intersection is before the robot
                if x > 0:
                    duration1 = (x - ROBOT_FLOOR_SENSOR_X) * 1000 / ROBOT_SETTINGS[memory.robot_id]["forward_speed"]
                    if duration1 < command.duration:
                        outcome_dict["duration1"] = round(duration1)
                        outcome_dict["color_index"] = cell_color(np.array([x, 0, 0]), memory)
                    else:
                        # Must reset the floor and yaw set above
                        outcome_dict["floor"] = 0
                        outcome_dict["yaw"] = 0
                    # Stop searching (assume the robot is inside the terrain)
                    break
        elif command.action.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD]:
            # Translate the shape by the position of the floor sensor so we can check the sign of the x coordinate
            ego_shape -= np.array([ROBOT_FLOOR_SENSOR_X, 0, 0])  #
            # Loop over the points where the x coordinate pass the floor sensor
            for i in np.where(np.diff(np.sign(ego_shape[:, 0])))[0]:
                if abs(ego_shape[i + 1][1] - ego_shape[i][1]) == 0:
                    y = ego_shape[i][1]
                else:
                    slope = (ego_shape[i + 1][0] - ego_shape[i][0]) / (ego_shape[i + 1][1] - ego_shape[i][1])
                    y = ego_shape[i][1] - ego_shape[i][0] / slope
                if command.speed[1] > 0 and y > 0:  # Swipe left
                    duration1 = y * 1000 / ROBOT_SETTINGS[memory.robot_id]["lateral_speed"]
                    if duration1 < command.duration:
                        outcome_dict["duration1"] = round(duration1)
                        outcome_dict["floor"] = 2
                        outcome_dict["yaw"] = RETREAT_YAW
                        outcome_dict["color_index"] = cell_color(np.array([ROBOT_FLOOR_SENSOR_X, y, 0]), memory)
                    break
                elif command.speed[1] < 0 and y < 0:  # Swipe right
                    duration1 = -y * 1000 / ROBOT_SETTINGS[memory.robot_id]["lateral_speed"]
                    if duration1 < command.duration:
                        outcome_dict["duration1"] = round(duration1)
                        outcome_dict["floor"] = 1
                        outcome_dict["yaw"] = -RETREAT_YAW
                        outcome_dict["color_index"] = cell_color(np.array([ROBOT_FLOOR_SENSOR_X, y, 0]), memory)
                    break

    # Compute the displacement in memory
    trajectory = Trajectory(memory, command)
    trajectory.track_displacement(command.yaw, Outcome(outcome_dict))

    # Apply the displacement to memory

    memory.allocentric_memory.move(memory.body_memory.body_quaternion, trajectory, command.clock)
    memory.body_memory.body_quaternion = memory.body_memory.body_quaternion.cross(trajectory.yaw_quaternion)
    memory.body_memory.head_direction_rad = trajectory.head_direction_rad
    memory.egocentric_memory.focus_point = trajectory.focus_point
    memory.egocentric_memory.prompt_point = trajectory.prompt_point

    # Push objects
    push_objects(trajectory, memory)

    # Predict the echo outcome from the nearest object phenomenon
    for p in [p for p in memory.phenomenon_memory.phenomena.values() if p.phenomenon_type == EXPERIENCE_ALIGNED_ECHO]:
        ego_center_point = memory.allocentric_to_egocentric(p.point)
        # # If the phenomenon is in front of the robot then the robot pushes it
        # if p.category is not None and ego_center_point[0] < ROBOT_FLOOR_SENSOR_X + p.category.short_radius and \
        #         abs(ego_center_point[1]) < ROBOT_OUTSIDE_Y:
        #     ego_center_point[0] = ROBOT_FLOOR_SENSOR_X + p.category.short_radius
        #     p.point = memory.egocentric_to_allocentric(ego_center_point)
        #     print("pushing object to ego position", ego_center_point)
        # if the phenomenon is recognized then subtract its radius to obtain the egocentric echo distance
        a, d = point_to_echo_direction_distance(ego_center_point)
        if p.category is not None:
            d -= p.category.short_radius
        if d > 0 and (command.action.action_code == ACTION_SCAN and assert_almost_equal_angles(math.radians(a), 0, 90)
                      or assert_almost_equal_angles(math.radians(a), memory.body_memory.head_direction_rad, 35)):
            outcome_dict["head_angle"] = round(a)
            outcome_dict["echo_distance"] = round(d)

    predicted_outcome = Outcome(outcome_dict)

    # Update focus based on echo
    trajectory.track_echo(predicted_outcome)

    code = outcome_code(memory, trajectory, predicted_outcome)

    return predicted_outcome, code


def cell_color(ego_point, memory):
    """Return the color index of the cell at the point provided in egocentric coordinates"""
    floor_i, floor_j = point_to_cell(memory.egocentric_to_allocentric(ego_point))
    if (memory.allocentric_memory.min_i <= floor_i <= memory.allocentric_memory.max_i) and \
            (memory.allocentric_memory.min_j <= floor_j <= memory.allocentric_memory.max_j) and \
            memory.allocentric_memory.grid[floor_i][floor_j].status[0] == EXPERIENCE_FLOOR:
        return memory.allocentric_memory.grid[floor_i][floor_j].color_index
    else:
        return 0


def push_objects(trajectory, memory):
    """Update the position of the phenomena that are on the robot's trajectory"""
    alo_covered_area = trajectory.covered_area + memory.allocentric_memory.robot_point
    path = mpath.Path(alo_covered_area[:, 0:2])
    for p in [p for p in memory.phenomenon_memory.phenomena.values() if p.category is not None and
              p.phenomenon_type == EXPERIENCE_ALIGNED_ECHO and path.contains_point(p.point[0:2])]:
        ego_point = memory.allocentric_to_egocentric(p.point)
        if ego_point[0] < ROBOT_FLOOR_SENSOR_X + p.category.short_radius and abs(ego_point[1]) < ROBOT_OUTSIDE_Y:
            ego_point[0] = ROBOT_FLOOR_SENSOR_X + p.category.short_radius
            p.point = memory.egocentric_to_allocentric(ego_point)
            # print("pushing object to ego position", ego_point)
