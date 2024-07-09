import math
import numpy as np
import time
import matplotlib.path as mpath
from ..Proposer.Action import ACTION_FORWARD, ACTION_SWIPE, ACTION_RIGHTWARD, ACTION_SCAN, ACTION_BACKWARD
from ..Memory.PhenomenonMemory import PHENOMENON_ENCLOSED_CONFIDENCE
from ..Memory.AllocentricMemory.Geometry import point_to_cell
from ..Memory.AllocentricMemory import STATUS_FLOOR, COLOR_INDEX
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_FLOOR
from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X, ROBOT_SETTINGS
from ..Robot.Outcome import Outcome
from ..Utils import assert_almost_equal_angles, point_to_head_direction_distance
from .Trajectory import Trajectory
from ..Integrator.OutcomeCode import outcome_code
from ..Memory.PhenomenonMemory import ARRANGE_OBJECT_RADIUS

# RETREAT_YAW = 35


def generate_prediction(command, memory):
    """Apply the command to memory. Return the predicted outcome."""

    # By default, predict the intended duration1, yaw, and floor: 0.
    outcome_dict = {"clock": command.clock, "action": command.action.action_code, "duration1": command.duration,
                    "head_angle": memory.body_memory.head_direction_degree()
                    # , "echo_distance": 10000  # not necessary
                    , "yaw": command.yaw, "floor": 0}

    # Predict crossing enclosed terrain

    if memory.phenomenon_memory.terrain_confidence() >= PHENOMENON_ENCLOSED_CONFIDENCE:
        # The shape of the terrain in egocentric coordinates
        ego_shape = np.apply_along_axis(memory.terrain_centric_to_egocentric, 1,
                                        memory.phenomenon_memory.terrain().shape)
        if command.action.action_code == ACTION_FORWARD:
            # Find the nearest intersection with the terrain on x axis
            intersections = []
            for i in np.where(np.diff(np.sign(ego_shape[:, 1])))[0]:
                intersection = x_intersection([ego_shape[i], ego_shape[i + 1]])
                if intersection is not None:
                    intersections.append(intersection)
            if len(intersections) > 0:
                closest_intersection = intersections[np.argmin(np.array(intersections)[:, 0])]
                duration1 = (closest_intersection[0] - ROBOT_FLOOR_SENSOR_X) * 1000 / ROBOT_SETTINGS[memory.robot_id]["forward_speed"]
                if duration1 < command.duration:
                    outcome_dict["duration1"] = round(duration1)
                    outcome_dict["floor"] = closest_intersection[1]
                    outcome_dict["color_index"] = cell_color(np.array([closest_intersection[0], 0, 0]), memory)
                    outcome_dict["confidence"] = memory.phenomenon_memory.terrain_confidence()
                    if closest_intersection[1] == 1:
                        outcome_dict["yaw"] = -memory.body_memory.retreat_yaw
                    elif closest_intersection[1] == 2:
                        outcome_dict["yaw"] = memory.body_memory.retreat_yaw
        elif command.action.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD]:
            # Translate the shape by the position of the floor sensor so we can check the sign of the x coordinate
            ego_shape -= np.array([ROBOT_FLOOR_SENSOR_X, 0, 0])  #
            # Loop over the points where the x coordinate pass the floor sensor
            intersections_left = []
            intersections_right = []
            for i in np.where(np.diff(np.sign(ego_shape[:, 0])))[0]:
                intersection = y_intersection([ego_shape[i], ego_shape[i + 1]])
                if intersection is not None:
                    if intersection > 0:
                        intersections_left.append(intersection)
                    else:
                        intersections_right.append(intersection)
            if command.speed[1] > 0 and len(intersections_left) > 0:  # Swipe left
                closest_intersection = intersections_left[np.argmin(np.array(intersections_left))]
                duration1 = closest_intersection * 1000 / ROBOT_SETTINGS[memory.robot_id]["lateral_speed"]
                if duration1 < command.duration:
                    outcome_dict["duration1"] = round(duration1)
                    outcome_dict["floor"] = 0b10
                    outcome_dict["yaw"] = memory.body_memory.retreat_yaw
                    outcome_dict["color_index"] = cell_color(np.array([ROBOT_FLOOR_SENSOR_X, closest_intersection, 0]), memory)
                    outcome_dict["confidence"] = memory.phenomenon_memory.terrain_confidence()
            elif command.speed[1] < 0 < len(intersections_right):  # Swipe right
                closest_intersection = intersections_right[np.argmax(np.array(intersections_right))]
                duration1 = -closest_intersection * 1000 / ROBOT_SETTINGS[memory.robot_id]["lateral_speed"]
                if duration1 < command.duration:
                    outcome_dict["duration1"] = round(duration1)
                    outcome_dict["floor"] = 0b01
                    outcome_dict["yaw"] = -memory.body_memory.retreat_yaw
                    outcome_dict["color_index"] = cell_color(np.array([ROBOT_FLOOR_SENSOR_X, closest_intersection, 0]), memory)
                    outcome_dict["confidence"] = memory.phenomenon_memory.terrain_confidence()

    # Predict crossing a dot phenomenon

    dots = [memory.allocentric_to_egocentric(p.point) for p in memory.phenomenon_memory.phenomena.values()
            if p.phenomenon_type == EXPERIENCE_FLOOR]
    # Test crossing dot phenomenon while moving forward
    if command.action.action_code == ACTION_FORWARD:
        dots = [p for p in dots if p[0] > ROBOT_FLOOR_SENSOR_X and abs(p[1]) < 20]
        if len(dots) > 0:
            closest_dot = dots[np.argmin(np.array(dots)[:, 0])]
            duration1 = (closest_dot[0] - ROBOT_FLOOR_SENSOR_X) * 1000 / ROBOT_SETTINGS[memory.robot_id]["forward_speed"]
            if duration1 < command.duration:
                record_dot_retreat(outcome_dict, duration1, closest_dot[1], memory.body_memory.retreat_yaw)
    # Test crossing dot phenomenon while moving backward
    elif command.action.action_code == ACTION_BACKWARD:
        dots = [p for p in dots if p[0] < ROBOT_FLOOR_SENSOR_X and abs(p[1]) < 20]
        if len(dots) > 0:
            closest_dot = dots[np.argmax(np.array(dots)[:, 0])]
            duration1 = (ROBOT_FLOOR_SENSOR_X - closest_dot[0]) * 1000 / ROBOT_SETTINGS[memory.robot_id]["forward_speed"]
            if duration1 < command.duration:
                record_dot_retreat(outcome_dict, duration1, closest_dot[1], memory.body_memory.retreat_yaw)

    # Compute the displacement in memory

    trajectory = Trajectory(memory, command)
    trajectory.track_displacement(Outcome(outcome_dict))

    # Push objects before moving the robot

    push_objects(trajectory, memory, outcome_dict["floor"])

    # Apply the displacement to memory

    memory.allocentric_memory.move(memory.body_memory.body_quaternion, trajectory, command.clock)
    memory.body_memory.body_quaternion = memory.body_memory.body_quaternion.cross(trajectory.yaw_quaternion)
    memory.body_memory.set_head_direction_degree(trajectory.head_direction_degree)
    memory.egocentric_memory.focus_point = trajectory.focus_point
    memory.egocentric_memory.prompt_point = trajectory.prompt_point

    # Predict the echo outcome from the first object phenomenon found in the sonar cone

    ad = [point_to_head_direction_distance(memory.allocentric_to_egocentric(p.point))
          for p in memory.phenomenon_memory.phenomena.values() if p.phenomenon_type == EXPERIENCE_ALIGNED_ECHO]
    scan_ad = np.array([p for p in ad if p[1] > 0 and (command.action.action_code == ACTION_SCAN and
                        assert_almost_equal_angles(math.radians(p[0]), 0, 125)
                        or assert_almost_equal_angles(math.radians(p[0]),
                                                      memory.body_memory.head_direction_rad, 35))], dtype=int)
    if scan_ad.ndim > 1:
        a, d = scan_ad[np.argmin(scan_ad[:, 1])].tolist()
        outcome_dict['head_angle'], outcome_dict['echo_distance'] = max(-90, min(a, 90)), d - ARRANGE_OBJECT_RADIUS
        # print("Predicted echo distance", outcome_dict['echo_distance'])
    elif trajectory.focus_point is not None:  # Focus not on an object
        outcome_dict['head_angle'], _ = point_to_head_direction_distance(trajectory.focus_point)
    outcome_dict['head_angle'] = round(max(-90, min(outcome_dict['head_angle'], 90)))

    predicted_outcome = Outcome(outcome_dict)

    # Update focus based on echo

    trajectory.track_focus(predicted_outcome)
    code = outcome_code(memory, trajectory, predicted_outcome)

    return predicted_outcome, code


def cell_color(ego_point, memory):
    """Return the color index of the cell at the point provided in egocentric coordinates"""
    floor_i, floor_j = point_to_cell(memory.egocentric_to_allocentric(ego_point))
    if (memory.allocentric_memory.min_i <= floor_i <= memory.allocentric_memory.max_i) and \
            (memory.allocentric_memory.min_j <= floor_j <= memory.allocentric_memory.max_j) and \
            memory.allocentric_memory.grid[floor_i][floor_j][STATUS_FLOOR] == EXPERIENCE_FLOOR:
        return int(memory.allocentric_memory.grid[floor_i][floor_j][COLOR_INDEX])
    else:
        return 0


def push_objects(trajectory, memory, floor):
    """Update the position of the phenomena that are on the robot's trajectory. Must be called before moving robot."""
    alo_covered_area = trajectory.covered_area + memory.allocentric_memory.robot_point
    path = mpath.Path(alo_covered_area[:, 0:2])
    for p in [p for p in memory.phenomenon_memory.phenomena.values() if p.category is not None and
              p.phenomenon_type == EXPERIENCE_ALIGNED_ECHO and path.contains_point(p.point[0:2])]:
        ego_point = memory.allocentric_to_egocentric(p.point)
        ego_point[0] = trajectory.translation[0] + ROBOT_FLOOR_SENSOR_X + p.category.short_radius
        # If floor then push beyond the retreat distance
        if floor:
            ego_point[0] += ROBOT_SETTINGS[memory.robot_id]["retreat_distance"][0]
        p.point = memory.egocentric_to_allocentric(ego_point)


def x_intersection(line):
    """Return the x value where the segment intersects the x axis, and the floor code"""
    # line1 = x1, y1, x2, y2
    x1, y1, x2, y2 = line[0][0], line[0][1], line[1][0], line[1][1]
    dx = (x2 - x1)
    if dx == 0:
        x = x1
        slope = np.inf
    else:
        slope = (y2 - y1) / dx
        x = x1 - y1 / slope

    if x < 0 or y1 * y2 > 0:
        # The line segment does not intersect before the robot
        return None
    if dx == 0 or abs(slope) > 10:
        # Line segment in front
        return [x, 3]
    elif (x1 < x2 and y1 < y2) or (x1 > x2 and y1 > y2):
        # Line segment to the right
        return [x, 1]
    else:
        # Line segment to the left
        return [x, 2]


def y_intersection(line):
    """Return the y value where the segment intersects the y axis or None"""
    # line1 = x1, y1, x2, y2
    x1, y1, x2, y2 = line[0][0], line[0][1], line[1][0], line[1][1]
    dy = (y2 - y1)
    if dy == 0:
        y = y1
    else:
        slope = (x2 - x1) / dy
        y = y1 - x1 / slope
    if x1 * x2 > 0:
        # The line segment does not intersect with the y axis
        return None
    else:
        return y


def record_dot_retreat(outcome_dict, duration1, closest_dot_y, retreat_yaw):
    """Record the retreat when crossed a DOT phenomenon"""
    outcome_dict["duration1"] = round(duration1)
    if closest_dot_y > 10:
        outcome_dict["floor"] = 0b10
        outcome_dict["yaw"] = retreat_yaw
    elif closest_dot_y > -10:
        outcome_dict["floor"] = 0b11
    else:
        outcome_dict["floor"] = 0b01
        outcome_dict["yaw"] = -retreat_yaw
