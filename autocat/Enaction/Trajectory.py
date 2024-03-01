import math
import numpy as np
from pyrr import matrix44, Vector3, Quaternion
from ..Decider.Action import ACTION_FORWARD
from ..Integrator.OutcomeCode import CONFIDENCE_NO_FOCUS, CONFIDENCE_NEW_FOCUS, CONFIDENCE_TOUCHED_FOCUS, \
    CONFIDENCE_CAREFUL_SCAN, CONFIDENCE_CONFIRMED_FOCUS
from ..Utils import short_angle, translation_quaternion_to_matrix, head_direction_distance_to_point, \
    point_to_echo_direction_distance
from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X, ROBOT_CHASSIS_Y, ROBOT_SETTINGS, ROBOT_CHASSIS_X, ROBOT_OUTSIDE_Y
from ..Memory.PhenomenonMemory import ARRANGE_OBJECT_RADIUS

FOCUS_MAX_DELTA = 200  # 200 (mm) Maximum delta to keep focus


class Trajectory:
    """Used to compute the displacement, and to keep track of the prompt and the focus"""
    def __init__(self, memory, command):
        """Record the initial conditions of this trajectory"""
        self.speed = command.speed
        self.span = command.span

        self.robot_id = memory.robot_id
        self.compass_offset = memory.body_memory.compass_offset

        # Track the displacement
        self.body_quaternion = memory.body_memory.body_quaternion.copy()
        self.head_direction_rad = memory.body_memory.head_direction_rad
        self.body_direction_delta = 0  # Displayed in BodyView
        self.focus_confidence = CONFIDENCE_NO_FOCUS  # Used by deciders to possibly trigger scan
        self.translation = None  # Used by allocentric memory to move the robot
        self.yaw_quaternion = None  # Used to compute yaw prediction error
        self.compass_quaternion = None  # Include the compass offset correction
        self.yaw_matrix = None  # Used by bodyView to rotate compass points
        self.displacement_matrix = None  # Used by EgocentricMemory to rotate experiences
        self.covered_area = np.empty((4, 3), dtype=int)

        # The prompt
        self.prompt_point = None
        if memory.egocentric_memory.prompt_point is not None:
            self.prompt_point = memory.egocentric_memory.prompt_point.copy()
        # The focus
        self.focus_point = None
        if memory.egocentric_memory.focus_point is not None:
            self.focus_point = memory.egocentric_memory.focus_point.copy()
        # print("Trajectory initial focus", self.focus_point)

    def track_displacement(self, intended_yaw, outcome):
        """Compute the displacement from the duration1, yaw, floor, impact"""

        # Translation integrated from the action's speed multiplied by the duration1
        self.translation = self.speed * outcome.duration1 / 1000

        # The area covered during the translation in polar-egocentric coordinates
        area = [[ROBOT_CHASSIS_X + max(0, self.translation[0]), ROBOT_OUTSIDE_Y + max(0, self.translation[1]), 0],
                [-ROBOT_CHASSIS_X + min(0, self.translation[0]), ROBOT_OUTSIDE_Y + max(0, self.translation[1]), 0],
                [-ROBOT_CHASSIS_X + min(0, self.translation[0]), -ROBOT_OUTSIDE_Y + min(0, self.translation[1]), 0],
                [ROBOT_CHASSIS_X + max(0, self.translation[0]), -ROBOT_OUTSIDE_Y + min(0, self.translation[1]), 0]]
        self.covered_area[:, :] = [(self.body_quaternion * Vector3(p)) for p in area]

        # The yaw quaternion
        if outcome.yaw is None:
            # If the yaw is not measured then use predicted yaw
            self.yaw_quaternion = Quaternion.from_z_rotation(math.radians(intended_yaw))
        else:
            self.yaw_quaternion = Quaternion.from_z_rotation(math.radians(outcome.yaw))

        # The new body quaternion computed by integrating the yaw (do not override body_quaternion yet)
        body_quaternion_integrated = self.body_quaternion.cross(self.yaw_quaternion)

        # If the robot returns no compass then the body_quaternion is estimated from yaw
        if outcome.compass_point is None:
            self.body_quaternion = body_quaternion_integrated
        else:
            # If the robot returns compass
            # Compute the compass_quaternion. Subtract the offset from robot_define.py
            outcome.compass_point -= self.compass_offset
            # The compass point indicates the south so we must take the opposite and rotate by pi/2
            body_direction_rad = math.atan2(-outcome.compass_point[0], -outcome.compass_point[1])
            self.compass_quaternion = Quaternion.from_z_rotation(body_direction_rad)

            if outcome.clock == 0:
                # On the first interaction, the body_quaternion is given by the compass
                self.body_quaternion = self.compass_quaternion
            else:
                # After the first interaction, the body_quaternion is averaged of the compass and the yaw integration
                if self.compass_quaternion.dot(body_quaternion_integrated) < 0.0:
                    body_quaternion_integrated = - body_quaternion_integrated

                # Save the difference to display in BodyView
                self.body_direction_delta = short_angle(self.compass_quaternion, body_quaternion_integrated)
                # If positive when turning trigonometric direction then the yaw is measured greater than it is

                # Take the median angle between the compass and the yaw estimate
                # 0 is compass only, 1 is yaw estimate only
                # This is known as a complementary filter
                # https://forum.arduino.cc/t/guide-to-gyro-and-accelerometer-with-arduino-including-kalman-filtering/57971
                body_quaternion_corrected = self.compass_quaternion.slerp(body_quaternion_integrated, 0.75)

                # Recompute the yaw quaternion
                self.yaw_quaternion = body_quaternion_corrected.cross(self.body_quaternion.inverse)
                if self.yaw_quaternion.angle > math.pi:
                    self.yaw_quaternion = -self.yaw_quaternion

                # Update the body_quaternion
                self.body_quaternion = body_quaternion_corrected

        # The retreat distance
        if outcome.floor > 0:
            front_point = Vector3([ROBOT_FLOOR_SENSOR_X, 0, 0])
            line_point = front_point + Vector3([ROBOT_SETTINGS[self.robot_id]["retreat_distance"], 0, 0])
            self.translation += front_point - self.yaw_quaternion * line_point

        if outcome.blocked:
            self.translation = np.array([0, 0, 0], dtype=int)

        # Compute the displacement matrix which represents the displacement of the environment
        # relative to the robot (Translates and turns in the opposite direction)
        self.yaw_matrix = matrix44.create_from_quaternion(self.yaw_quaternion)
        self.displacement_matrix = translation_quaternion_to_matrix(-self.translation, self.yaw_quaternion.inverse)

        # Move the focus
        if self.focus_point is not None:
            self.focus_point = matrix44.apply_to_vector(self.displacement_matrix, self.focus_point).astype(int)
            # Keep head towards focus
            self.head_direction_rad = min(max(-math.pi/2, math.atan2(self.focus_point[1], self.focus_point[0])), math.pi/2)

        # Move the prompt
        if self.prompt_point is not None:
            self.prompt_point = matrix44.apply_to_vector(self.displacement_matrix, self.prompt_point).astype(int)

    def track_focus(self, outcome):
        """Compute the focus_confidence and adjust it to new echo"""

        new_echo = outcome.echo_point
        # If careful watch and there are central echoes then the focus is the first (closest)
        if self.span == 10 and len(outcome.central_echos) > 0:
            new_echo = head_direction_distance_to_point(*outcome.central_echos[0])

        # The new focus is at the center of the object  TODO must recognize the object
        if new_echo is None:
            new_focus = None
        else:
            a, d = point_to_echo_direction_distance(new_echo)
            new_focus = head_direction_distance_to_point(a, d + ARRANGE_OBJECT_RADIUS)

        # If the robot was focussed then adjust the focus and the displacement
        if self.focus_point is not None:
            if new_focus is not None:
                # The error between the expected and the actual position of the echo
                prediction_error_focus = self.focus_point - new_focus
                # If the new focus is near the previous focus or the displacement has been continuous.
                if np.linalg.norm(prediction_error_focus) < FOCUS_MAX_DELTA or outcome.status == "continuous":
                    # The focus has been kept
                    # print("Focus kept with prediction error", prediction_error_focus, "moved to ", new_focus)
                    self.focus_confidence = CONFIDENCE_CONFIRMED_FOCUS
                else:
                    # The focus was lost
                    # print("Focus delta:", prediction_error_focus, "New focus:", new_focus)
                    self.focus_confidence = CONFIDENCE_NEW_FOCUS
            else:
                # The focus was lost
                # print("Lost focus due to no echo ", new_focus)
                self.focus_confidence = CONFIDENCE_NO_FOCUS
                # self.head_direction_rad = math.atan2(self.focus_point[1], self.focus_point[0])  # look at old focus

        # If the robot was not focussed then check for catch focus
        elif new_focus is not None:
            # if outcome.action_code in [ACTION_SCAN, ACTION_FORWARD, ACTION_TURN, ACTION_WATCH] \
            #         and outcome.echo_point is not None:
            # Catch focus
            self.focus_confidence = CONFIDENCE_NEW_FOCUS
            # print("New focus ", new_focus)

        self.focus_point = new_focus
        if new_focus is not None:
            self.head_direction_rad = min(max(-math.pi/2, math.atan2(new_focus[1], new_focus[0])), math.pi/2)

        # Careful scan has extra confidence
        if self.focus_confidence == CONFIDENCE_NEW_FOCUS and self.span == 10:
            self.focus_confidence = CONFIDENCE_CAREFUL_SCAN

        # Impact or block catch focus
        if outcome.impact > 0 and outcome.action_code == ACTION_FORWARD:
            if new_focus is None or np.linalg.norm(new_focus) > 200:
                # Focus on the object "felt"
                if outcome.impact == 0b01:
                    self.focus_point = np.array([ROBOT_FLOOR_SENSOR_X + 10, -ROBOT_CHASSIS_Y, 0])
                elif outcome.impact == 0b10:
                    self.focus_point = np.array([ROBOT_FLOOR_SENSOR_X + 10, ROBOT_CHASSIS_Y, 0])
                else:
                    self.focus_point = np.array([ROBOT_FLOOR_SENSOR_X + 10, 0, 0])
            self.focus_confidence = CONFIDENCE_TOUCHED_FOCUS
            # print("Catch focus impact", self.focus_point)
