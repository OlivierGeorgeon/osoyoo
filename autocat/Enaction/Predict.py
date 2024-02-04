import math
import numpy as np
from pyrr import matrix44, Quaternion, Vector3
from ..Decider.Action import ACTION_FORWARD, ACTION_SWIPE, ACTION_RIGHTWARD, ACTION_SCAN
from ..Memory.PhenomenonMemory import PHENOMENON_RECOGNIZED_CONFIDENCE
from ..Memory.PhenomenonMemory.PhenomenonMemory import BOX
from ..Memory.AllocentricMemory.Hexagonal_geometry import point_to_cell
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_FLOOR
from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X, ROBOT_SETTINGS
from ..Robot.Outcome import Outcome
from ..Memory.BodyMemory import point_to_echo_direction_distance
from ..Utils import assert_almost_equal_angles, translation_quaternion_to_matrix

RETREAT_YAW = 45


def predict_outcome(command, memory):
    """Return the predicted outcome of executing this command in this memory"""

    # By default, predict the intended duration1, yaw, and floor: 0.
    predicted_outcome = {"clock": command.clock, "action": command.action.action_code, "duration1": command.duration,
                         "yaw": command.yaw, "floor": 0}

    # If terrain is recognized, adjust the floor, duration1, and yaw outcome
    if memory.phenomenon_memory.terrain_confidence() >= PHENOMENON_RECOGNIZED_CONFIDENCE:
        # The shape of the terrain in egocentric coordinates
        ego_shape = np.array([memory.terrain_centric_to_egocentric(p) for p in memory.phenomenon_memory.terrain().shape])
        if command.action.action_code == ACTION_FORWARD:
            # Loop over the points where the y coordinate changes sign
            for i in np.where(np.diff(np.sign(ego_shape[:, 1])))[0]:
                # find the x coordinate of the line intersection. Tentatively set floor and yaw
                if abs(ego_shape[i + 1][0] - ego_shape[i][0]) < 5:
                    predicted_outcome["floor"] = 3
                    predicted_outcome["yaw"] = 0
                    x = ego_shape[i][0]
                else:
                    slope = (ego_shape[i + 1][1] - ego_shape[i][1]) / (ego_shape[i + 1][0] - ego_shape[i][0])
                    x = ego_shape[i][0] - ego_shape[i][1] / slope
                    if ego_shape[i][0] > ego_shape[i + 1][0]:
                        predicted_outcome["floor"] = 1
                        predicted_outcome["yaw"] = -RETREAT_YAW
                    else:
                        predicted_outcome["floor"] = 2
                        predicted_outcome["yaw"] = RETREAT_YAW
                # If the line intersection is before the robot
                if x > 0:
                    duration1 = (x - ROBOT_FLOOR_SENSOR_X) * 1000 / ROBOT_SETTINGS[memory.robot_id]["forward_speed"]
                    if duration1 < command.duration:
                        predicted_outcome["duration1"] = round(duration1)
                        predicted_outcome["color_index"] = cell_color(np.array([x, 0, 0]), memory)
                    else:
                        # Must reset the floor and yaw set above
                        predicted_outcome["floor"] = 0
                        predicted_outcome["yaw"] = 0
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
                        predicted_outcome["duration1"] = round(duration1)
                        predicted_outcome["floor"] = 2
                        predicted_outcome["yaw"] = RETREAT_YAW
                        predicted_outcome["color_index"] = cell_color(np.array([ROBOT_FLOOR_SENSOR_X, y, 0]), memory)
                    break
                elif command.speed[1] < 0 and y < 0:  # Swipe right
                    duration1 = -y * 1000 / ROBOT_SETTINGS[memory.robot_id]["lateral_speed"]
                    if duration1 < command.duration:
                        predicted_outcome["duration1"] = round(duration1)
                        predicted_outcome["floor"] = 1
                        predicted_outcome["yaw"] = -RETREAT_YAW
                        predicted_outcome["color_index"] = cell_color(np.array([ROBOT_FLOOR_SENSOR_X, y, 0]), memory)
                    break

    # Compute the displacement in memory

    translation = command.speed * predicted_outcome["duration1"] / 1000
    yaw_quaternion = Quaternion.from_z_rotation(math.radians(predicted_outcome["yaw"]))
    # yaw_quaternion = command.intended_yaw_quaternion
    if predicted_outcome["floor"] > 0:
        front_point = Vector3([ROBOT_FLOOR_SENSOR_X, 0, 0])
        line_point = front_point + Vector3([ROBOT_SETTINGS[memory.robot_id]["retreat_distance"], 0, 0])
        translation += front_point - yaw_quaternion * line_point
    displacement_matrix = translation_quaternion_to_matrix(-translation, yaw_quaternion.inverse)

    # Apply the displacement to memory

    memory.allocentric_memory.move(memory.body_memory.body_quaternion, translation, command.clock)
    memory.body_memory.body_quaternion = memory.body_memory.body_quaternion.cross(yaw_quaternion)
    # memory.body_memory.body_quaternion = command.intended_yaw_quaternion * memory.body_memory.body_quaternion  # works
    if memory.egocentric_memory.prompt_point is not None:
        memory.egocentric_memory.prompt_point = \
            matrix44.apply_to_vector(displacement_matrix, memory.egocentric_memory.prompt_point).astype(int)
    if memory.egocentric_memory.focus_point is not None:
        memory.egocentric_memory.focus_point = \
            matrix44.apply_to_vector(displacement_matrix, memory.egocentric_memory.focus_point).astype(int)
        a, _ = point_to_echo_direction_distance(memory.egocentric_memory.focus_point)
        memory.body_memory.head_direction_rad = a

    # Predict the echo outcome from the nearest object phenomenon

    predicted_outcome["head_angle"] = memory.body_memory.head_direction_degree()
    predicted_outcome["echo_distance"] = 10000
    for p in [p for p in memory.phenomenon_memory.phenomena.values()
              if p.phenomenon_type == EXPERIENCE_ALIGNED_ECHO]:
        ego_center_point = memory.allocentric_to_egocentric(p.point)
        a, d = point_to_echo_direction_distance(ego_center_point)
        # Subtract the phenomenon's radius to obtain the egocentric echo distance
        d -= memory.phenomenon_memory.phenomenon_categories[BOX].long_radius
        if d > 0 and command.action.action_code == ACTION_SCAN and assert_almost_equal_angles(math.radians(a), 0, 90) \
                or assert_almost_equal_angles(math.radians(a), memory.body_memory.head_direction_rad, 35):
            predicted_outcome["head_angle"] = round(a)
            predicted_outcome["echo_distance"] = round(d)

    return Outcome(predicted_outcome)


def cell_color(ego_point, memory):
    """Return the color index of the cell at the point provided in egocentric coordinates"""
    floor_i, floor_j = point_to_cell(memory.egocentric_to_allocentric(ego_point))
    # print("Color in cell (", floor_i, floor_j, ")")
    if (memory.allocentric_memory.min_i <= floor_i <= memory.allocentric_memory.max_i) and \
            (memory.allocentric_memory.min_j <= floor_j <= memory.allocentric_memory.max_j) and \
            memory.allocentric_memory.grid[floor_i][floor_j].status[0] == EXPERIENCE_FLOOR:
        return memory.allocentric_memory.grid[floor_i][floor_j].color_index
    else:
        return 0
