import json
import math
import numpy as np
from pyrr import matrix44, Quaternion
from playsound import playsound
from ..Decider.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_LEFTWARD, ACTION_RIGHTWARD, \
    ACTION_TURN, ACTION_TURN_RIGHT, ACTION_TURN_HEAD, ACTION_SCAN, ACTION_WATCH
from ..Memory.Memory import SIMULATION_STEP_ON, SIMULATION_TIME_RATIO
from .RobotDefine import DEFAULT_YAW, TURN_DURATION, ROBOT_FRONT_X, ROBOT_FRONT_Y
from .Command import Command

FOCUS_MAX_DELTA = 100  # 200 (mm) Maximum delta to keep focus


class Enaction:
    """An Enaction object handles the enaction of an interaction by the robot
    1. Workspace instantiates an intended_interaction
    2. CtrlRobot send a serialization of the intended_interaction to the robot
    3. CtrlRobot instantiates an enacted_interaction using the outcome recieved from the robot
    4. CtrlRobot call enacted_interaction.follow_up(intended_interaction) to update the focus and the azimuth

    """
    def __init__(self, action, clock, memory):
        # The intended enaction
        self.action = action
        self.clock = clock
        # self.duration = None
        # self.angle = None
        self.prompt_point = None
        self.focus_point = None
        # self.body_direction_rad = 0
        self.body_quaternion = None
        self.command = None
        # if memory is not None:
        if memory.egocentric_memory.prompt_point is not None:
            self.prompt_point = memory.egocentric_memory.prompt_point.copy()
        if memory.egocentric_memory.focus_point is not None:
            self.focus_point = memory.egocentric_memory.focus_point.copy()
        self.command = Command(self.action, self.clock, self.prompt_point, self.focus_point)
        # self.body_direction_rad = memory.body_memory.get_body_direction_rad()
        self.body_quaternion = memory.body_memory.body_quaternion
        assert(type(self.body_quaternion) == Quaternion)


        # The simulation of the enaction in memory
        self.simulation_duration = 0
        self.simulation_rotation_speed = 0
        self.simulation_step = 0
        self.simulation_time = 0.

        # The enacted enaction
        self.outcome = None
        # self.status = "0"
        # self.duration1 = 0
        # self.yaw = 0
        # self.compass_point = None
        # self.azimuth = None  # Remains None if the robot does not return azimuth or compass
        self.body_direction_delta = 0
        # self.echo_point = None
        self.lost_focus = False
        # self.floor = 0
        # self.impact = 0
        # self.blocked = False
        # self.color_index = 0
        # self.head_angle = 0
        # self.echos = {}
        # self.compass_quaternion = None
        self.translation = None
        # self.translation = np.array([0, 0, 0], dtype=float)
        # self.rotation_matrix = matrix44.create_from_z_rotation(self.yaw)
        self.displacement_matrix = None #matrix44.multiply(self.rotation_matrix, matrix44.create_from_translation(-self.translation))

    def start_simulation(self):
        """Initialize the simulation of the intended interaction"""
        self.simulation_step = SIMULATION_STEP_ON
        # Compute the duration and the speed depending and the enaction
        self.simulation_duration = self.action.target_duration
        self.simulation_rotation_speed = self.action.rotation_speed_rad
        if self.command.duration is not None:
            # self.simulation_duration = self.duration / 1000
            self.simulation_duration = self.command.duration / 1000
        if self.command.angle is not None:
            self.simulation_duration = math.fabs(self.command.angle) * TURN_DURATION / DEFAULT_YAW
            if self.command.angle < 0 and self.action.action_code != ACTION_TURN_RIGHT:  # TODO fix turn right with prompt
                self.simulation_rotation_speed = -self.action.rotation_speed_rad
        self.simulation_duration *= SIMULATION_TIME_RATIO
        self.simulation_rotation_speed *= SIMULATION_TIME_RATIO

    # def body_label(self):
    #     """Return the label to display in the body view"""
    #     rotation_speed = "{:.2f}".format(math.degrees(self.action.rotation_speed_rad))
    #     label = "Speed x: " + str(int(self.action.translation_speed[0])) + "mm/s, y: " \
    #         + str(int(self.action.translation_speed[1])) + "mm/s, rotation:" + rotation_speed + "°/s"
    #     return label
    #
    # def body_label_azimuth(self):
    #     """Return the label to display in the body view"""
    #     azimuth = round((90 - math.degrees(self.body_direction_rad)) % 360)
    #     if self.azimuth is None:
    #         return "Azimuth: " + str(azimuth)
    #     else:
    #         return "Azimuth: " + str(azimuth) + ", compass: " + str(self.azimuth) + ", delta: " + \
    #                "{:.2f}".format(math.degrees(self.body_direction_delta))
    #
    def follow_up(self, outcome):
        """Manage focus catch, lost, or update.
        Move the prompt
        Update the azimuth"""
        self.outcome = outcome

        # The displacement --------

        # Translation integrated from the action's speed multiplied by the duration1
        # TODO Take the yaw into account
        self.translation = self.action.translation_speed * (float(outcome.duration1) / 1000.0)
        self.translation += outcome.retreat_translation
        if outcome.blocked:
            translation = np.array([0, 0, 0], dtype=int)

        # The yaw quaternion
        if outcome.yaw_quaternion is None:
            yaw_quaternion = Quaternion.from_z_rotation(self.action.target_duration * math.degrees(self.action.rotation_speed_rad))
        else:
            yaw_quaternion = outcome.yaw_quaternion

        yaw_integration_quaternion = self.body_quaternion.cross(yaw_quaternion)

        # If the robot returns no compass then the body_quaternion is estimated from yaw
        if outcome.compass_point is None:
            self.body_quaternion = yaw_integration_quaternion
        else:
            # Subtract the offset from robot_define.py
            # compass_point = outcome.compass_point - self.workspace.memory.body_memory.compass_offset
            # The compass point indicates the south so we must take the opposite and rotate by pi/2
            # body_direction_rad = math.atan2(-compass_point[0], -compass_point[1])
            # self.compass_quaternion = Quaternion.from_z_rotation(math.atan2(-compass_point[0], -compass_point[1]))
            # The compass point indicates the south so we must rotate it of 180° to obtain the azimuth
            # self.azimuth = round(math.degrees(math.atan2(self.compass_point[0], self.compass_point[1])) + 180) % 360

            # Reinitialize the body_quaternion from the compass
            # self.body_quaternion = self.outcome.compass_quaternion
            # After the first interaction, the body_quaternion is averaged between the compass and the yaw integration
            if self.clock == 0:
                self.body_quaternion = self.outcome.compass_quaternion
            else:
                if self.outcome.compass_quaternion.dot(yaw_integration_quaternion) < 0.0:
                    yaw_integration_quaternion = - yaw_integration_quaternion

                # Save the difference
                dif_q = self.outcome.compass_quaternion.cross(yaw_integration_quaternion.inverse)
                if dif_q.angle > math.pi:
                    dif_q = -dif_q
                self.body_direction_delta = dif_q.axis[2] * dif_q.angle

                # Take the median angle between the compass and the yaw estimate
                # 0 is compass only, 1 is yaw estimate only
                new_body_quaternion = self.outcome.compass_quaternion.slerp(yaw_integration_quaternion, 0.5)

                # The yaw quaternion is recomputed
                yaw_quaternion = new_body_quaternion.cross(self.body_quaternion.inverse)
                if yaw_quaternion.angle > math.pi:
                    yaw_quaternion = -yaw_quaternion
                self.body_quaternion = new_body_quaternion

        # Compute the displacement matrix which represents the relative displacement of the environment
        # relative to the robot (Translates and turns in the opposite direction)
        yaw_matrix = matrix44.create_from_quaternion(yaw_quaternion)
        self.displacement_matrix = matrix44.multiply(matrix44.create_from_translation(-self.translation), yaw_matrix)

        # The focus --------

        # If the robot is already focussed then adjust the focus and the displacement
        if self.focus_point is not None:
            # The new estimated position of the focus point
            # displacement_matrix = self.displacement_matrix
            # translation = self.translation
            # rotation_matrix = self.rotation_matrix
            if self.outcome.echo_point is not None:
                # action_code = enacted_enaction.action.action_code
                # The error between the expected and the actual position of the echo
                prediction_focus_point = matrix44.apply_to_vector(self.displacement_matrix, self.focus_point)
                prediction_error_focus = prediction_focus_point - self.outcome.echo_point
                # If the new focus is near the previous focus or the displacement has been continuous.
                if np.linalg.norm(prediction_error_focus) < FOCUS_MAX_DELTA or self.outcome.status == "continuous":
                    # The focus has been kept
                    self.focus_point = self.outcome.echo_point
                    print("UPDATE FOCUS by delta", prediction_error_focus)
                    # enacted_enaction.is_focussed = True
                    # If the action has been completed
                    if self.outcome.duration1 >= 1000:
                        # If the head is forward then correct longitudinal displacements
                        if -20 < self.outcome.head_angle < 20:
                            if self.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
                                self.translation[0] = self.translation[0] + prediction_error_focus[0]
                                # Correct the estimated speed of the action
                                self.action.adjust_translation_speed(self.translation)
                        # If the head is sideways then correct lateral displacements
                        if self.outcome.head_angle < -60 or 60 < self.outcome.head_angle:
                            if self.action.action_code in [ACTION_LEFTWARD, ACTION_RIGHTWARD]:
                                self.translation[1] = self.translation[1] + prediction_error_focus[1]
                                # Correct the estimated speed of the action
                                self.action.adjust_translation_speed(self.translation)
                        # Update the displacement matrix according to the new translation
                        translation_matrix = matrix44.create_from_translation(-self.translation)
                        # displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
                        self.displacement_matrix = matrix44.multiply(translation_matrix, yaw_matrix)
                        # self.translation = translation
                        # self.displacement_matrix = displacement_matrix
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
            if self.action.action_code in [ACTION_SCAN, ACTION_FORWARD, ACTION_TURN, ACTION_WATCH] \
                    and self.outcome.echo_point is not None:
                # Catch focus
                playsound('autocat/Assets/cute_beep2.wav', False)
                self.focus_point = self.outcome.echo_point
                print("CATCH FOCUS", self.focus_point)

        # Impact or block catch focus
        if self.outcome.impact > 0 and self.action.action_code == ACTION_FORWARD:  # or enacted_enaction.blocked:
            if self.outcome.echo_point is None or np.linalg.norm(self.outcome.echo_point) > 200:
                # Count as an echo to to activate DeciderCircle
                if self.outcome.impact == 0b01:
                    self.focus_point = np.array([ROBOT_FRONT_X + 10, -ROBOT_FRONT_Y, 0])
                elif self.outcome.impact == 0b10:
                    self.focus_point = np.array([ROBOT_FRONT_X + 10, ROBOT_FRONT_Y, 0])
                else:
                    self.focus_point = np.array([ROBOT_FRONT_X + 10, 0, 0])
            else:
                self.focus_point = self.outcome.echo_point
            # Reset lost focus to activate DecideCircle
            self.lost_focus = False
            print("CATCH FOCUS IMPACT", self.focus_point)

        # Move the prompt
        if self.prompt_point is not None:
            self.prompt_point = matrix44.apply_to_vector(self.displacement_matrix, self.prompt_point).astype(int)
            print("Prompt moved to egocentric: ", self.prompt_point)

        # Estimate the new azimuth from the yaw
        # yaw_quaternion = Quaternion.from_z_rotation(math.radians(self.yaw))
        # estimate_body_quaternion = intended_enaction.body_quaternion.cross(yaw_quaternion)
        #
        # # If the robot returns no azimuth then the body_quaternion is estimated from yaw
        # if self.azimuth is None:
        #     self.body_quaternion = estimate_body_quaternion
        # else:
        #     # If the robot returns the azimuth then the body_quaternion is initialized from the azimuth
        #     self.body_quaternion = Quaternion.from_z_rotation(self.body_direction_rad)
        #     # After the first interaction, the body_quaternion is averaged between the compass and the estimate
        #     if self.clock > 0:
        #         dot = self.body_quaternion.dot(estimate_body_quaternion)
        #         if dot < 0.0:
        #             estimate_body_quaternion = - estimate_body_quaternion
        #
        #         # Save the difference
        #         dif_q = self.body_quaternion.cross(estimate_body_quaternion.inverse)
        #         if dif_q.angle > math.pi:
        #             dif_q = -dif_q
        #         self.body_direction_delta = dif_q.axis[2] * dif_q.angle
        #
        #         # Take the median angle between the compass and the yaw estimate
        #         # 0 is compass only, 1 is yaw estimate only
        #         self.body_quaternion = self.body_quaternion.slerp(estimate_body_quaternion, 0.5)
        # self.body_direction_rad = self.body_quaternion.axis[2] * self.body_quaternion.angle
        # print("Computed body direction:", round(math.degrees(self.body_direction_rad)))
