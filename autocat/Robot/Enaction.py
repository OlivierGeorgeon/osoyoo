import json
import math
import numpy as np
from pyrr import matrix44, quaternion
from playsound import playsound
from ..Decider.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_ALIGN_ROBOT, ACTION_LEFTWARD, ACTION_RIGHTWARD, \
    ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_TURN_HEAD, ACTION_SCAN
from ..Memory.Memory import SIMULATION_STEP_ON, SIMULATION_TIME_RATIO
from .RobotDefine import DEFAULT_YAW, TURN_DURATION, ROBOT_FRONT_X, ROBOT_FRONT_Y

ENACTION_DEFAULT_TIMEOUT = 6  # Seconds
FOCUS_MAX_DELTA = 100  # 200 (mm) Maximum delta to keep focus


class Enaction:
    def __init__(self, action, clock, memory):
        # The intended enaction
        self.action = action
        self.clock = clock
        self.duration = None
        self.angle = None
        self.focus_point = None
        self.prompt_point = None
        self.body_direction_rad = 0
        self.body_quaternion = None  # Inferred from compass and yaw
        if memory is not None:
            if memory.egocentric_memory.focus_point is not None:
                self.focus_point = memory.egocentric_memory.focus_point.copy()
            if memory.egocentric_memory.prompt_point is not None:
                self.prompt_point = memory.egocentric_memory.prompt_point.copy()
                if self.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
                    self.duration = int(np.linalg.norm(self.prompt_point) /
                                        math.fabs(self.action.translation_speed[0]) * 1000)
                if self.action.action_code in [ACTION_LEFTWARD, ACTION_RIGHTWARD]:
                    self.duration = int(np.linalg.norm(self.prompt_point) /
                                        math.fabs(self.action.translation_speed[1]) * 1000)
                if self.action.action_code in [ACTION_ALIGN_ROBOT, ACTION_TURN_HEAD]:
                    self.angle = int(math.degrees(math.atan2(self.prompt_point[1], self.prompt_point[0])))
                if (self.action.action_code == ACTION_TURN_RIGHT) and self.prompt_point[1] < 0:
                    self.angle = int(math.degrees(math.atan2(self.prompt_point[1], self.prompt_point[0])))
                if (self.action.action_code == ACTION_TURN_LEFT) and self.prompt_point[1] > 0:
                    self.angle = int(math.degrees(math.atan2(self.prompt_point[1], self.prompt_point[0])))
            else:
                # Default backward 0.5s
                if self.action.action_code in [ACTION_BACKWARD]:
                    self.duration = 500
                # Default sidewards 1.5s
                if self.action.action_code in [ACTION_LEFTWARD, ACTION_RIGHTWARD]:
                    self.duration = 1000  # 1500
            self.body_direction_rad = memory.body_memory.get_body_direction_rad()
            self.body_quaternion = memory.body_memory.body_quaternion  # Inferred from compass and yaw

        # The simulation of the enaction in memory
        self.simulation_duration = 0
        self.simulation_rotation_speed = 0
        self.simulation_step = 0
        self.simulation_time = 0.

        # The enacted enaction
        self.status = None
        self.duration1 = 0
        self.yaw = 0
        self.compass_point = None
        self.azimuth = None  # Remains None if the robot does not return azimuth or compass
        self.body_direction_delta = 0
        self.echo_point = None
        self.lost_focus = False
        self.floor = 0
        self.impact = 0
        self.blocked = False
        self.color_index = 0
        self.head_angle = 0
        self.echos = {}
        self.translation = np.array([0, 0, 0], dtype=float)
        self.rotation_matrix = matrix44.create_from_z_rotation(self.yaw)
        self.displacement_matrix = matrix44.multiply(self.rotation_matrix,
                                                     matrix44.create_from_translation(-self.translation))

    def serialize(self):
        """Return the serial representation to send to the robot"""
        serial = {'clock': self.clock, 'action': self.action.action_code}
        if self.duration is not None:
            serial['duration'] = self.duration
        if self.angle is not None:
            serial['angle'] = self.angle
        if self.focus_point is not None:
            serial['focus_x'] = int(self.focus_point[0])  # Convert to python int
            serial['focus_y'] = int(self.focus_point[1])
        if self.action.action_code == ACTION_FORWARD:
            serial['speed'] = int(self.action.translation_speed[0])
        if self.action.action_code == ACTION_BACKWARD:
            serial['speed'] = -int(self.action.translation_speed[0])
        if self.action.action_code == ACTION_LEFTWARD:
            serial['speed'] = int(self.action.translation_speed[1])
        if self.action.action_code == ACTION_RIGHTWARD:
            serial['speed'] = -int(self.action.translation_speed[1])
        return json.dumps(serial)

    def timeout(self):
        """Return the timeout of this enaction"""
        timeout = ENACTION_DEFAULT_TIMEOUT
        if self.duration is not None:
            timeout = self.duration / 1000.0 + 4.0
        if self.angle is not None:
            timeout = math.fabs(self.angle) / DEFAULT_YAW + 4.0  # Turn speed = 45°/s
        return timeout

    def start_simulation(self):
        """Initialize the simulation of the intended interaction"""
        self.simulation_step = SIMULATION_STEP_ON
        # Compute the duration and the speed depending and the enaction
        self.simulation_duration = self.action.target_duration
        self.simulation_rotation_speed = self.action.rotation_speed_rad
        if self.duration is not None:
            self.simulation_duration = self.duration / 1000
        if self.angle is not None:
            self.simulation_duration = math.fabs(self.angle) * TURN_DURATION / DEFAULT_YAW
            if self.angle < 0 and self.action.action_code != ACTION_TURN_RIGHT:  # TODO fix turn right with prompt
                self.simulation_rotation_speed = -self.action.rotation_speed_rad
        self.simulation_duration *= SIMULATION_TIME_RATIO
        self.simulation_rotation_speed *= SIMULATION_TIME_RATIO

    def body_label(self):
        """Return the label to display in the body view"""
        rotation_speed = "{:.2f}".format(math.degrees(self.action.rotation_speed_rad))
        label = "Speed x: " + str(int(self.action.translation_speed[0])) + "mm/s, y: " \
            + str(int(self.action.translation_speed[1])) + "mm/s, rotation:" + rotation_speed + "°/s"
        return label

    def body_label_azimuth(self):
        """Return the label to display in the body view"""
        azimuth = round((90 - math.degrees(self.body_direction_rad)) % 360)
        if self.azimuth is None:
            return "Azimuth: " + str(azimuth)
        else:
            return "Azimuth: " + str(azimuth) + ", compass: " + str(self.azimuth) + ", delta: " + \
                   " {:.2f}".format(math.degrees(self.body_direction_delta))

    def follow_up(self, intended_enaction):
        """Manage focus catch, lost, or update. Also move the prompt"""

        # If the robot is already focussed then adjust the focus and the displacement
        if intended_enaction.focus_point is not None:
            # The new estimated position of the focus point
            displacement_matrix = self.displacement_matrix
            translation = self.translation
            rotation_matrix = self.rotation_matrix
            if self.echo_point is not None:
                # action_code = enacted_enaction.action.action_code
                # The error between the expected and the actual position of the echo
                prediction_focus_point = matrix44.apply_to_vector(displacement_matrix, intended_enaction.focus_point)
                prediction_error_focus = prediction_focus_point - self.echo_point
                # If the new focus is near the previous focus
                if np.linalg.norm(prediction_error_focus) < FOCUS_MAX_DELTA:
                    # The focus has been kept
                    self.focus_point = self.echo_point
                    print("UPDATE FOCUS by delta", prediction_error_focus)
                    # enacted_enaction.is_focussed = True
                    # If the action has been completed
                    if self.duration1 >= 1000:
                        # If the head is forward then correct longitudinal displacements
                        if -20 < self.head_angle < 20:
                            if self.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
                                translation[0] = translation[0] + prediction_error_focus[0]
                                # Correct the estimated speed of the action
                                self.action.adjust_translation_speed(translation)
                        # If the head is sideways then correct lateral displacements
                        if self.head_angle < -60 or 60 < self.head_angle:
                            if self.action.action_code in [ACTION_LEFTWARD, ACTION_RIGHTWARD]:
                                translation[1] = translation[1] + prediction_error_focus[1]
                                # Correct the estimated speed of the action
                                self.action.adjust_translation_speed(translation)
                        # Update the displacement matrix according to the new translation
                        translation_matrix = matrix44.create_from_translation(-translation)
                        # displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
                        displacement_matrix = matrix44.multiply(translation_matrix, rotation_matrix)
                        self.translation = translation
                        self.displacement_matrix = displacement_matrix
                else:
                    # The focus was lost
                    print("LOST FOCUS due to delta", prediction_error_focus)
                    self.lost_focus = True  # Used by agent_circle
                    self.focus_point = None
                    # playsound('autocat/Assets/R5.wav', False)
            else:
                # The focus was lost
                print("LOST FOCUS due to no echo")
                self.lost_focus = True  # Used by agent_circle
                self.focus_point = None
                # playsound('autocat/Assets/R5.wav', False)
        else:
            # If the robot was not focussed
            if self.action.action_code in [ACTION_SCAN, ACTION_FORWARD] \
                    and self.echo_point is not None:
                # Catch focus
                playsound('autocat/Assets/cute_beep2.wav', False)
                self.focus_point = self.echo_point
                print("CATCH FOCUS", self.focus_point)

        # Impact or block catch focus
        if self.impact > 0 and self.action.action_code == ACTION_FORWARD:  # or enacted_enaction.blocked:
            if self.echo_point is None or np.linalg.norm(self.echo_point) > 200:
                # Count as an echo to to activate DeciderCircle
                if self.impact == 0b01:
                    self.focus_point = np.array([ROBOT_FRONT_X + 10, -ROBOT_FRONT_Y, 0])
                elif self.impact == 0b10:
                    self.focus_point = np.array([ROBOT_FRONT_X + 10, ROBOT_FRONT_Y, 0])
                else:
                    self.focus_point = np.array([ROBOT_FRONT_X + 10, 0, 0])
            else:
                self.focus_point = self.echo_point
            # Reset lost focus to activate DecideCircle
            self.lost_focus = False
            print("CATCH FOCUS IMPACT", self.focus_point)

        # Move the prompt
        if intended_enaction.prompt_point is not None:
            self.prompt_point = matrix44.apply_to_vector(self.displacement_matrix, intended_enaction.prompt_point).astype(int)
            print("Prompt moved to egocentric: ", self.prompt_point)

        # Estimate the new azimuth from the yaw
        yaw_quaternion = quaternion.create_from_z_rotation(math.radians(self.yaw))
        estimate_body_quaternion = quaternion.cross(intended_enaction.body_quaternion, yaw_quaternion)

        # If the robot returns no azimuth then the body_quaternion is estimated from yaw
        if self.azimuth is None:
            self.body_quaternion = estimate_body_quaternion
        else:
            # If the robot returns the azimuth then the body_quaternion is initialized from the azimuth
            self.body_quaternion = quaternion.create_from_z_rotation(self.body_direction_rad)
            # After the first interaction, the body_quaternion is averaged between the compass and the estimate
            if self.clock > 0:
                dot = quaternion.dot(self.body_quaternion, estimate_body_quaternion)
                if dot < 0.0:
                    estimate_body_quaternion = - estimate_body_quaternion

                # Print the difference
                dif_q = quaternion.cross(self.body_quaternion, quaternion.inverse(estimate_body_quaternion))
                if quaternion.rotation_angle(dif_q) > math.pi:
                    dif_q = -dif_q
                # if quaternion.rotation_axis(dif_q)[2] > 0:
                #     print("difference angle", math.degrees(quaternion.rotation_angle(dif_q)))
                # else:
                #     print("difference angle", -math.degrees(quaternion.rotation_angle(dif_q)))
                # Used to calibrate GYRO_COEF
                self.body_direction_delta = quaternion.rotation_axis(dif_q)[2] * quaternion.rotation_angle(dif_q)

                # Take the median angle between the compass and the yaw estimate
                # 0 is compass only, 1 is yaw estimate only
                self.body_quaternion = quaternion.slerp(self.body_quaternion, estimate_body_quaternion, 0.5)
        self.body_direction_rad = quaternion.rotation_axis(self.body_quaternion)[2] * \
                                  quaternion.rotation_angle(self.body_quaternion)
        # print("Computed body direction:", round(math.degrees(self.body_direction_rad)))
