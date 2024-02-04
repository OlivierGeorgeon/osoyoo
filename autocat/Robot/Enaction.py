import math
import numpy as np
from pyrr import matrix44, Vector3, Quaternion
from playsound import playsound
from ..Decider.Action import ACTION_FORWARD, ACTION_TURN, ACTION_SCAN, ACTION_WATCH
from ..Decider.Decider import CONFIDENCE_NO_FOCUS, CONFIDENCE_NEW_FOCUS, CONFIDENCE_TOUCHED_FOCUS, \
    CONFIDENCE_CAREFUL_SCAN, CONFIDENCE_CONFIRMED_FOCUS
from ..Memory.BodyMemory import point_to_echo_direction_distance
from ..Utils import short_angle, translation_quaternion_to_matrix
from .RobotDefine import ROBOT_FLOOR_SENSOR_X, ROBOT_CHASSIS_Y, ROBOT_SETTINGS
from .Command import Command, DIRECTION_FRONT
from .Outcome import echo_point
from ..Enaction.Predict import predict_outcome
from ..Enaction.Trajectory import Trajectory


class Enaction:
    """An Enaction object handles the enaction of an interaction by the robot
    1. Workspace instantiates the enaction
    2. CtrlRobot sends the command to the robot
    3. CtrlRobot computes the outcome received from the robot
    4. CtrlRobot call ternminate(outcome)
    """
    def __init__(self, action, memory, direction=DIRECTION_FRONT, span=40, caution=0):
        """Initialize the enaction upon creation. Will be adjusted before generating the command"""
        # The initial arguments
        self.action = action
        # self.robot_id = memory.robot_id
        self.clock = memory.clock
        # self.compass_offset = memory.body_memory.compass_offset

        # # Copy spatial modifiers
        # self.body_quaternion = memory.body_memory.body_quaternion.copy()
        # self.prompt_point = None
        # if memory.egocentric_memory.prompt_point is not None:
        #     self.prompt_point = memory.egocentric_memory.prompt_point.copy()
        # self.focus_point = None
        # if memory.egocentric_memory.focus_point is not None:
        #     self.focus_point = memory.egocentric_memory.focus_point.copy()

        # Generate the command to the robot
        self.command = Command(self.action, self.clock, memory.egocentric_memory.prompt_point,
                               memory.egocentric_memory.focus_point, direction, span, memory.emotion_code, caution)

        # Initialize the predicted memory
        self.predicted_memory = memory.save()
        self.predicted_memory.clock += 1

        # Compute the predicted outcome and update the predicted memory
        self.predicted_outcome = predict_outcome(self.command, self.predicted_memory)

        # Initialize the trajectory
        self.trajectory = Trajectory(memory, self.predicted_outcome.yaw, self.command.speed, self.command.span)

        # The actual outcome
        self.outcome = None

        # # The trajectory
        # self.body_direction_delta = 0  # Displayed in BodyView
        # self.focus_confidence = CONFIDENCE_NO_FOCUS  # Used by deciders to possibly trigger scan
        # self.translation = None  # Used by allocentric memory to move the robot
        # self.yaw_quaternion = None  # Used to compute yaw prediction error
        # self.compass_quaternion = None  # Include the compass offset correction
        # self.yaw_matrix = None  # Used by bodyView to rotate compass points
        # self.displacement_matrix = None  # Used by EgocentricMemory to rotate experiences
        # # self.line_point = None
        # self.focus_direction_prediction_error = 0
        # self.focus_distance_prediction_error = 0

        # The message received from other robot
        self.message = None
        # Message sent to other robots
        self.message_sent = False

    def begin(self, body_quaternion):
        """Adjust the spatial modifiers of the enaction.
        Compute the command to send to the robot.
        Initialize the simulation"""

        print("Command", self.command.serialize())
        print("Predicted outcome", self.predicted_outcome)
        # Update the body_quaternion to avoid errors in the estimated yaw
        self.trajectory.body_quaternion = body_quaternion.copy()

    def terminate(self, outcome):
        """Computes the body_quaternion, the translation, the displacement_matrix, the focus and the prompt."""
        self.outcome = outcome

        self.trajectory.terminate(self.outcome)

        # # The displacement --------
        #
        # # Translation integrated from the action's speed multiplied by the duration1
        # self.translation = self.command.speed * self.outcome.duration1 / 1000
        #
        # # The yaw quaternion
        # if outcome.yaw is None:
        #     # If the yaw is not measured then use predicted yaw TODO recompute yaw if floor
        #     self.yaw_quaternion = Quaternion.from_z_rotation(math.radians(self.predicted_outcome.yaw))
        # else:
        #     self.yaw_quaternion = Quaternion.from_z_rotation(math.radians(self.outcome.yaw))
        #
        # # The new body quaternion computed by integrating the yaw (do not override body_quaternion yet)
        # body_quaternion_integrated = self.body_quaternion.cross(self.yaw_quaternion)
        #
        # # If the robot returns no compass then the body_quaternion is estimated from yaw
        # if outcome.compass_point is None:
        #     self.body_quaternion = body_quaternion_integrated
        # else:
        #     # If the robot returns compass
        #     # Compute the compass_quaternion. Subtract the offset from robot_define.py
        #     self.outcome.compass_point -= self.compass_offset
        #     # The compass point indicates the south so we must take the opposite and rotate by pi/2
        #     body_direction_rad = math.atan2(-self.outcome.compass_point[0], -self.outcome.compass_point[1])
        #     self.compass_quaternion = Quaternion.from_z_rotation(body_direction_rad)
        #
        #     if self.clock == 0:
        #         # On the first interaction, the body_quaternion is given by the compass
        #         self.body_quaternion = self.compass_quaternion
        #     else:
        #         # After the first interaction, the body_quaternion is averaged of the compass and the yaw integration
        #         if self.compass_quaternion.dot(body_quaternion_integrated) < 0.0:
        #             body_quaternion_integrated = - body_quaternion_integrated
        #
        #         # Save the difference to display in BodyView
        #         self.body_direction_delta = short_angle(self.compass_quaternion, body_quaternion_integrated)
        #         # If positive when turning trigonometric direction then the yaw is measured greater than it is
        #
        #         # Take the median angle between the compass and the yaw estimate
        #         # 0 is compass only, 1 is yaw estimate only
        #         # This is known as a complementary filter
        #         # https://forum.arduino.cc/t/guide-to-gyro-and-accelerometer-with-arduino-including-kalman-filtering/57971
        #         body_quaternion_corrected = self.compass_quaternion.slerp(body_quaternion_integrated, 0.75)
        #
        #         # Recompute the yaw quaternion
        #         self.yaw_quaternion = body_quaternion_corrected.cross(self.body_quaternion.inverse)
        #         if self.yaw_quaternion.angle > math.pi:
        #             self.yaw_quaternion = -self.yaw_quaternion
        #
        #         # Update the body_quaternion
        #         self.body_quaternion = body_quaternion_corrected
        #
        # # The retreat distance
        # if self.outcome.floor > 0:
        #     front_point = Vector3([ROBOT_FLOOR_SENSOR_X, 0, 0])
        #     line_point = front_point + Vector3([ROBOT_SETTINGS[self.robot_id]["retreat_distance"], 0, 0])
        #     self.translation += front_point - self.yaw_quaternion * line_point
        #     playsound('autocat/Assets/cyberpunk3.wav', False)
        #
        # if outcome.blocked:
        #     self.translation = np.array([0, 0, 0], dtype=int)
        #
        # # Compute the displacement matrix which represents the displacement of the environment
        # # relative to the robot (Translates and turns in the opposite direction)
        # self.yaw_matrix = matrix44.create_from_quaternion(self.yaw_quaternion)
        # self.displacement_matrix = translation_quaternion_to_matrix(-self.translation, self.yaw_quaternion.inverse)
        #
        # # The focus --------
        #
        # # If careful watch then the focus is the first central_echo
        # new_focus = self.outcome.echo_point
        # if self.command.span == 10 and len(self.outcome.central_echos) > 0:
        #     new_focus = echo_point(*self.outcome.central_echos[0])
        #
        # # If the robot is already focussed then adjust the focus and the displacement
        # if self.focus_point is not None:
        #     if new_focus is not None:
        #         # The error between the expected and the actual position of the echo
        #         new_focus_direction, new_focus_distance = point_to_echo_direction_distance(new_focus)
        #         prediction_focus_point = matrix44.apply_to_vector(self.displacement_matrix, self.focus_point)
        #         prediction_focus_direction, prediction_focus_distance = point_to_echo_direction_distance(prediction_focus_point)
        #         prediction_error_focus = prediction_focus_point - new_focus
        #         self.focus_direction_prediction_error = prediction_focus_direction - new_focus_direction
        #         self.focus_distance_prediction_error = prediction_focus_distance - new_focus_distance
        #         # If the new focus is near the previous focus or the displacement has been continuous.
        #         if np.linalg.norm(prediction_error_focus) < FOCUS_MAX_DELTA or self.outcome.status == "continuous":
        #             # The focus has been kept
        #             print("Focus kept with prediction error", prediction_error_focus, "moved to ", end="")
        #             self.focus_confidence = CONFIDENCE_CONFIRMED_FOCUS
        #             # If the action has been completed
        #             # if self.outcome.duration1 >= 1000:
        #             #     # If the head is forward then correct longitudinal displacements
        #             #     if -20 < self.outcome.head_angle < 20:
        #             #         if self.action.action_code in [ACTION_FORWARD, ACTION_BACKWARD]:
        #             #             self.translation[0] = self.translation[0] + prediction_error_focus[0]
        #             #             # Correct the estimated speed of the action
        #             #             if self.command.duration is None:
        #             #                 self.action.adjust_translation_speed(self.translation)
        #             #     # If the head is sideways then correct lateral displacements
        #             #     if self.outcome.head_angle < -60 or 60 < self.outcome.head_angle:
        #             #         if self.action.action_code in [ACTION_SWIPE, ACTION_RIGHTWARD]:
        #             #             self.translation[1] = self.translation[1] + prediction_error_focus[1]
        #             #             # Correct the estimated speed of the action
        #             #             if self.command.duration is None:
        #             #                 self.action.adjust_translation_speed(self.translation)
        #             #     # Update the displacement matrix according to the new translation
        #             #     translation_matrix = matrix44.create_from_translation(-self.translation)
        #             #     self.displacement_matrix = matrix44.multiply(translation_matrix, self.yaw_matrix)
        #         else:
        #             # The focus was lost
        #             print("Focus delta:", prediction_error_focus, "New focus:", end="")
        #             # Careful scan forces CONFIDENCE_CAREFUL_SCAN
        #             # if self.command.span == 10:
        #             #     self.focus_confidence = CONFIDENCE_CAREFUL_SCAN
        #             # else:
        #             self.focus_confidence = CONFIDENCE_NEW_FOCUS
        #             # playsound('autocat/Assets/R5.wav', False)
        #     else:
        #         # The focus was lost
        #         print("Lost focus due to no echo ", end="")
        #         self.focus_confidence = CONFIDENCE_NO_FOCUS
        #         # playsound('autocat/Assets/R5.wav', False)
        # else:
        #     # If the robot was not focussed then check for catch focus
        #     if self.action.action_code in [ACTION_SCAN, ACTION_FORWARD, ACTION_TURN, ACTION_WATCH] \
        #             and self.outcome.echo_point is not None:
        #         # Catch focus
        #         # playsound('autocat/Assets/cute_beep2.wav', False)  # DeciderExplore and DeciderWatch often clear focus
        #         self.focus_confidence = CONFIDENCE_NEW_FOCUS
        #         print("New focus ", end="")
        # self.focus_point = new_focus
        # print("Focus point", self.focus_point)
        #
        # # Careful scan has extra confidence
        # if self.focus_confidence == CONFIDENCE_NEW_FOCUS and self.command.span == 10:
        #     self.focus_confidence = CONFIDENCE_CAREFUL_SCAN
        #
        # # Impact or block catch focus
        # if self.outcome.impact > 0 and self.action.action_code == ACTION_FORWARD:
        #     if new_focus is None or np.linalg.norm(new_focus) > 200:
        #         # Focus on the object "felt"
        #         if self.outcome.impact == 0b01:
        #             self.focus_point = np.array([ROBOT_FLOOR_SENSOR_X + 10, -ROBOT_CHASSIS_Y, 0])
        #         elif self.outcome.impact == 0b10:
        #             self.focus_point = np.array([ROBOT_FLOOR_SENSOR_X + 10, ROBOT_CHASSIS_Y, 0])
        #         else:
        #             self.focus_point = np.array([ROBOT_FLOOR_SENSOR_X + 10, 0, 0])
        #     self.focus_confidence = CONFIDENCE_TOUCHED_FOCUS
        #     print("Catch focus impact", self.focus_point)
        #
        # # Move the prompt -----
        # if self.prompt_point is not None:
        #     self.prompt_point = matrix44.apply_to_vector(self.displacement_matrix, self.prompt_point).astype(int)

    def succeed(self):
        """Return True if the enaction succeeded: no floor or impact outcome"""
        return self.outcome.floor == 0 and self.outcome.impact == 0

    def current_enaction(self):
        """Used if the enaction is taken as a composite enaction"""
        return self

    def increment(self):
        """Used if the enaction is taken as a composite enaction"""
        return False
