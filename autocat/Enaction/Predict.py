import numpy as np
from ..Decider.Action import ACTION_FORWARD, ACTION_SWIPE, ACTION_RIGHTWARD
from ..Memory.PhenomenonMemory import PHENOMENON_RECOGNIZED_CONFIDENCE
from ..Memory.AllocentricMemory.Hexagonal_geometry import point_to_cell
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_FLOOR
from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X, ROBOT_SETTINGS

RETREAT_YAW = 45


def predict_outcome(command, memory):
    """Return the predicted outcome of executing this command in this memory"""

    # By default, predict the intended duration1, yaw, and floor: 0.
    predicted_outcome = {"clock": command.clock, "action": command.action.action_code, "duration1": command.duration,
                         "yaw": command.yaw, "floor": 0, "status": "P"}

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
                    x_line = ego_shape[i][0]
                else:
                    slope = (ego_shape[i + 1][1] - ego_shape[i][1]) / (ego_shape[i + 1][0] - ego_shape[i][0])
                    x_line = ego_shape[i][0] - ego_shape[i][1] / slope
                    if ego_shape[i][0] > ego_shape[i + 1][0]:
                        predicted_outcome["floor"] = 1
                        predicted_outcome["yaw"] = -RETREAT_YAW
                    else:
                        predicted_outcome["floor"] = 2
                        predicted_outcome["yaw"] = RETREAT_YAW
                # If the line intersection is before the robot
                if x_line > 0:
                    # print("intersection point", memory.phenomenon_memory.terrain().shape[i], "Distance", x_line)
                    duration1 = (x_line - ROBOT_FLOOR_SENSOR_X) * 1000 / ROBOT_SETTINGS[memory.robot_id]["forward_speed"]
                    if duration1 < command.duration:
                        predicted_outcome["duration1"] = round(duration1)
                        predicted_outcome["color_index"] = cell_color(np.array([x_line, 0, 0]), memory)
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
                    y_line = ego_shape[i][1]
                else:
                    slope = (ego_shape[i + 1][0] - ego_shape[i][0]) / (ego_shape[i + 1][1] - ego_shape[i][1])
                    y_line = ego_shape[i][1] - ego_shape[i][0] / slope
                if command.speed_y > 0 and y_line > 0:  # Swipe left
                    duration1 = y_line * 1000 / ROBOT_SETTINGS[memory.robot_id]["lateral_speed"]
                    if duration1 < command.duration:
                        predicted_outcome["duration1"] = round(duration1)
                        predicted_outcome["floor"] = 2
                        predicted_outcome["yaw"] = RETREAT_YAW
                        predicted_outcome["color_index"] = cell_color(np.array([ROBOT_FLOOR_SENSOR_X, y_line, 0]), memory)
                    break
                elif command.speed_y < 0 and y_line < 0:  # Swipe right
                    duration1 = -y_line * 1000 / ROBOT_SETTINGS[memory.robot_id]["lateral_speed"]
                    if duration1 < command.duration:
                        predicted_outcome["duration1"] = round(duration1)
                        predicted_outcome["floor"] = 1
                        predicted_outcome["yaw"] = -RETREAT_YAW
                        predicted_outcome["color_index"] = cell_color(np.array([ROBOT_FLOOR_SENSOR_X, y_line, 0]), memory)
                    break
    return predicted_outcome


def cell_color(ego_point, memory):
    """Return the color index of the cell at the point provided in egocentric coordinates"""
    floor_i, floor_j = point_to_cell(memory.egocentric_to_allocentric(ego_point))
    print("Color in cell (", floor_i, floor_j, ")")
    if (memory.allocentric_memory.min_i <= floor_i <= memory.allocentric_memory.max_i) and \
            (memory.allocentric_memory.min_j <= floor_j <= memory.allocentric_memory.max_j) and \
            memory.allocentric_memory.grid[floor_i][floor_j].status[0] == EXPERIENCE_FLOOR:
        return memory.allocentric_memory.grid[floor_i][floor_j].color_index
    else:
        return 0
