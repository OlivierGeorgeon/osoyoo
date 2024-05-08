import math
import numpy as np
import matplotlib
import os
import csv
from pyrr import Quaternion
from ..Proposer.Action import ACTION_FORWARD, ACTION_BACKWARD, ACTION_SWIPE
from ..Proposer.Interaction import OUTCOME_LOST_FOCUS, OUTCOME_NO_FOCUS, OUTCOME_FLOOR
from ..Utils import short_angle, point_to_head_direction_distance
from .PlotSequence import plot

PREDICTION_ERROR_WINDOW = 200
RUNNING_AVERAGE_COEF = 0.25


class PredictionError:
    def __init__(self, workspace):
        """Initialize the prediction error arrays"""
        self.workspace = workspace
        self.pe_outcome_code = {}
        self.pe_forward_duration1 = {}  # (s)
        self.pe_lateral_duration1 = {}  # (s)
        self.pe_yaw = {}  # (degree)
        self.re_yaw = {}  # (degree)
        self.re_compass = {}  # (degree)
        self.pe_echo_direction = {}  # (degree)
        self.pe_echo_distance = {}  # (mm)
        self.pe_focus_direction = {}  # (degree)
        self.pe_focus_distance = {}  # (mm)

        self.pe_speed_forward = {}  # (mm/s)
        self.value_speed_forward = {}  # (mm/s)
        self.pe_speed_backward = {}  # (mm/s)
        self.value_speed_backward = {}  # (mm/s)
        self.pe_x_speed = {}  # (mm/s)
        self.x_speed = {}  # (mm/s)
        self.pe_y_speed = {}  # (mm/s)
        self.y_speed = {}  # (mm/s)

        self.previous_echo_distance = 0
        self.previous_echo_point = None
        self.previous_yaw_re = 100  # To check that reduction error decreases

        # The agg backend avoids interfering with pyglet windows
        # https://matplotlib.org/stable/users/explain/figure/backends.html
        matplotlib.use('agg')
        # Create the log directory if it does not exist because it is not included in git
        if not os.path.exists("log"):
            os.makedirs("log")

    def log(self, enaction):
        """Compute the prediction errors: computed - actual"""
        computed_outcome = enaction.predicted_outcome
        actual_outcome = enaction.outcome

        # Outcome code
        pe = int(enaction.predicted_outcome_code != enaction.outcome_code)
        self.pe_outcome_code[enaction.clock] = pe
        self.pe_outcome_code.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
        print("Prediction Error Outcome Code",
              f"(predicted:{enaction.predicted_outcome_code}, actual:{enaction.outcome_code})= {pe}",
              f"Average: {np.mean(list(self.pe_outcome_code.values())):.1f}",
              f"std: {np.std(list(self.pe_outcome_code.values())):.1f}")

        # Translation FORWARD duration1

        if enaction.action.action_code in [ACTION_FORWARD] and actual_outcome.duration1 != 0:
            pe = (computed_outcome.duration1 - actual_outcome.duration1) / 1000  # / actual_outcome.duration1
            self.pe_forward_duration1[enaction.clock] = pe
            self.pe_forward_duration1.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
            print(f"Prediction Error Translate duration1 (simulation - measured)= {pe:.3f}",
                  f"Average: {np.mean(list(self.pe_forward_duration1.values())):.3f}",
                  f"std: {np.std(list(self.pe_forward_duration1.values())):.3f}")

            # Forward speed

            self.value_speed_forward[enaction.clock] = self.workspace.actions[ACTION_FORWARD].translation_speed[0]
            self.x_speed[enaction.clock] = self.workspace.actions[ACTION_FORWARD].translation_speed[0]
            if abs(actual_outcome.head_angle) < 11 and \
                    enaction.outcome_code not in [OUTCOME_LOST_FOCUS, OUTCOME_NO_FOCUS, OUTCOME_FLOOR]:
                action_speed = self.workspace.actions[ACTION_FORWARD].translation_speed[0]
                speed = (self.previous_echo_distance - actual_outcome.echo_distance) * 1000 / actual_outcome.duration1
                pe = round(action_speed - speed)
                self.pe_speed_forward[enaction.clock] = pe
                self.pe_speed_forward.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
                print(f"Prediction Error Speed (simulation {action_speed:.0f}, - measured {speed:.0f})= {pe}",
                      "Average:", round(float(np.mean(list(self.pe_speed_forward.values()))), 1),
                      "std:", round(float(np.std(list(self.pe_speed_forward.values())))), 1)
                # Update the speed of the action
                self.workspace.actions[ACTION_FORWARD].translation_speed[0] = action_speed * (1. - RUNNING_AVERAGE_COEF) + speed * RUNNING_AVERAGE_COEF

                # Use the same speed forward and backward
                self.pe_x_speed[enaction.clock] = pe
                self.pe_x_speed.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
                print(f"Prediction Error X Speed (simulation {action_speed:.0f}, - measured {speed:.0f})= {pe}",
                      "Average:", round(float(np.mean(list(self.pe_x_speed.values()))), 1),
                      "std:", round(float(np.std(list(self.pe_x_speed.values())))), 1)
                self.workspace.actions[ACTION_BACKWARD].translation_speed[0] = - action_speed * (1. - RUNNING_AVERAGE_COEF) - speed * RUNNING_AVERAGE_COEF

        # Translation Backward

        if enaction.action.action_code in [ACTION_BACKWARD] and actual_outcome.duration1 != 0 and \
                enaction.outcome_code not in [OUTCOME_LOST_FOCUS, OUTCOME_NO_FOCUS, OUTCOME_FLOOR]:
            self.value_speed_backward[enaction.clock] = self.workspace.actions[ACTION_BACKWARD].translation_speed[0]
            self.x_speed[enaction.clock] = -self.workspace.actions[ACTION_BACKWARD].translation_speed[0]
            # if assert_almost_equal_angles(math.radians(actual_outcome.head_angle), 0, 11):
            if abs(actual_outcome.head_angle) < 11:
                action_speed = self.workspace.actions[ACTION_BACKWARD].translation_speed[0]
                speed = (self.previous_echo_distance - actual_outcome.echo_distance) * 1000 / actual_outcome.duration1
                pe = round(action_speed - speed)
                self.pe_speed_backward[enaction.clock] = pe
                self.pe_speed_backward.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
                print(f"Prediction Error Speed Back (simulation {action_speed:.0f}, - measured {speed:.0f})= {pe}",
                      "Average:", round(float(np.mean(list(self.pe_speed_backward.values()))), 1),
                      "std:", round(float(np.std(list(self.pe_speed_backward.values())))), 1)
                # Update the speed of the action
                self.workspace.actions[ACTION_BACKWARD].translation_speed[0] = action_speed * (1. - RUNNING_AVERAGE_COEF) + speed * RUNNING_AVERAGE_COEF
                # Use the same speed forward and backward
                self.pe_x_speed[enaction.clock] = - pe  # Opposite
                self.pe_x_speed.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
                print(f"Prediction Error X Speed (simulation {action_speed:.0f}, - measured {speed:.0f})= {pe}",
                      "Average:", round(float(np.mean(list(self.pe_x_speed.values()))), 1),
                      "std:", round(float(np.std(list(self.pe_x_speed.values())))), 1)
                # Update the action speed
                self.workspace.actions[ACTION_FORWARD].translation_speed[0] = - action_speed * (1. - RUNNING_AVERAGE_COEF) - speed * RUNNING_AVERAGE_COEF

        self.previous_echo_distance = actual_outcome.echo_distance

        # Swipe

        if enaction.action.action_code in [ACTION_SWIPE] and actual_outcome.duration1 != 0:
            self.y_speed[enaction.clock] = enaction.action.translation_speed[1]
            pe = (computed_outcome.duration1 - actual_outcome.duration1) / 1000  # / actual_outcome.duration1
            self.pe_lateral_duration1[enaction.clock] = pe
            self.pe_lateral_duration1.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
            print(f"Prediction Error Swipe duration1 (simulation - measured)= {pe:.3f}",
                  f"Average: {np.mean(list(self.pe_lateral_duration1.values())):.2f}",
                  f"std: {np.std(list(self.pe_lateral_duration1.values())):.2f}")

            # If focus and head toward object  TODO test that
            if enaction.outcome_code not in [OUTCOME_LOST_FOCUS, OUTCOME_NO_FOCUS, OUTCOME_FLOOR] and \
                    abs(actual_outcome.head_angle) > 80 and self.previous_echo_point is not None:
                action_speed = enaction.action.translation_speed[1]
                speed = abs(self.previous_echo_point[1] - actual_outcome.echo_point[1]) * 1000 / actual_outcome.duration1
                pe = round(action_speed - speed)
                self.pe_y_speed[enaction.clock] = pe
                self.pe_y_speed.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
                print(f"Prediction Error Y Speed (simulation {action_speed:.0f}, - measured {speed:.0f})= {pe}",
                      f"Average: {np.mean(list(self.pe_y_speed.values())):.1f}",
                      f"std: {np.std(list(self.pe_y_speed.values())):.1f}")
                # Update the action speed
                self.workspace.actions[ACTION_SWIPE].translation_speed[1] = action_speed * (1. - RUNNING_AVERAGE_COEF) + speed * RUNNING_AVERAGE_COEF

        if actual_outcome.echo_point is not None:
            self.previous_echo_point = actual_outcome.echo_point.copy()
        else:
            self.previous_echo_point = None

        # Yaw raw prediction error

        # if enaction.outcome.floor == 0 and enaction.predicted_outcome.floor == 0:
        pe = math.degrees(-short_angle(Quaternion.from_z_rotation(math.radians(computed_outcome.yaw)),
                                       enaction.trajectory.yaw_quaternion))
        self.pe_yaw[enaction.clock] = pe
        self.pe_yaw.pop(enaction.clock - PREDICTION_ERROR_WINDOW, None)
        print(f"Prediction Error Yaw (command - measure)= {pe:.1f} Average: {np.mean(list(self.pe_yaw.values())):.1f}",
              f"std: {np.std(list(self.pe_yaw.values())):.1f}")

        # Yaw residual error

        if enaction.outcome.floor in [1, 2]:
            if enaction.outcome.floor == 1:
                q_computed = Quaternion.from_z_rotation(math.radians(-self.workspace.memory.body_memory.retreat_yaw))
            else:
                q_computed = Quaternion.from_z_rotation(math.radians(self.workspace.memory.body_memory.retreat_yaw))
            re = math.degrees(-short_angle(q_computed, enaction.trajectory.yaw_quaternion))
            self.re_yaw[enaction.clock] = re
            self.re_yaw.pop(enaction.clock - PREDICTION_ERROR_WINDOW, None)
            print(f"Residual Error Withdraw Yaw (computed - measured)= {re:.1f}",
                  f"Average: {np.mean(list(self.re_yaw.values())):.1f}",
                  f"std: {np.std(list(self.re_yaw.values())):.1f}")
            # If residual error increased then decrease serotonine (not fun!)
            if abs(self.previous_yaw_re) <= abs(re):
                self.workspace.memory.body_memory.serotonin = max(40, self.workspace.memory.body_memory.serotonin - 1)
            self.previous_yaw_re = re
        elif enaction.outcome.floor == 3:  # not fun either
            self.workspace.memory.body_memory.serotonin = max(40, self.workspace.memory.body_memory.serotonin - 1)

        # Compass residual error

        self.re_compass[enaction.clock] = math.degrees(enaction.trajectory.body_direction_delta)
        self.re_compass.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
        print("Residual Error Compass (integrated direction - compass measure)=",
              round(self.re_compass[enaction.clock], 2), "Average:",
              round(float(np.mean(list(self.re_compass.values()))), 2), "std:",
              round(float(np.std(list(self.re_compass.values()))), 2))

        # The echo prediction error when focus is confident

        # if enaction.trajectory.focus_confidence >= CONFIDENCE_CONFIRMED_FOCUS:
        pe = computed_outcome.head_angle - actual_outcome.head_angle
        self.pe_echo_direction[actual_outcome.clock] = pe
        self.pe_echo_direction.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
        print("Prediction Error Head Direction (prediction - measure)=", pe,
              # enaction.trajectory.focus_direction_prediction_error,
              "Average:", round(float(np.mean(list(self.pe_echo_direction.values())))),
              "std:", round(float(np.std(list(self.pe_echo_direction.values())))))

        if computed_outcome.echo_distance < 10000 and actual_outcome.echo_distance < 10000:
            pe = computed_outcome.echo_distance - actual_outcome.echo_distance
            self.pe_echo_distance[enaction.clock] = pe
            self.pe_echo_distance.pop(enaction.clock - PREDICTION_ERROR_WINDOW, None)
            print("Prediction Error Echo Distance (prediction - measure)=", pe,
                  # enaction.trajectory.focus_distance_prediction_error,
                  "Average:", round(float(np.mean(list(self.pe_echo_distance.values())))),
                  "std:", round(float(np.std(list(self.pe_echo_distance.values())))))

        # The focus prediction error

        if enaction.predicted_memory.egocentric_memory.focus_point is not None and enaction.trajectory.focus_point is not None:
            pa, pd = point_to_head_direction_distance(enaction.predicted_memory.egocentric_memory.focus_point)
            ma, md = point_to_head_direction_distance(enaction.trajectory.focus_point)
            self.pe_focus_direction[actual_outcome.clock] = round(pa - ma)
            self.pe_focus_direction.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
            print("Prediction Error Focus Direction (prediction - measure)=", round(pa - ma),
                  "Average:", round(float(np.mean(list(self.pe_focus_direction.values())))),
                  "std:", round(float(np.std(list(self.pe_focus_direction.values())))))
            self.pe_focus_distance[enaction.clock] = round(pd - md)
            self.pe_focus_distance.pop(enaction.clock - PREDICTION_ERROR_WINDOW, None)
            print("Prediction Error Focus Distance (prediction - measure)=", round(pd - md),
                  "Average:", round(float(np.mean(list(self.pe_focus_distance.values())))),
                  "std:", round(float(np.std(list(self.pe_focus_distance.values())))))

        # The terrain origin prediction error

        terrain = self.workspace.memory.phenomenon_memory.terrain()
        if terrain is not None:
            terrain.origin_prediction_error.pop(enaction.clock - PREDICTION_ERROR_WINDOW, None)
            if enaction.clock in terrain.origin_prediction_error:
                print("Prediction Error Terrain origin (integration - measure)=",
                      round(terrain.origin_prediction_error[enaction.clock]),
                      "Average:", round(float(np.mean(list(terrain.origin_prediction_error.values())))),
                      "std:", round(float(np.std(list(terrain.origin_prediction_error.values())))))

        # Trace the enaction
        position_pe = ""
        if self.workspace.memory.phenomenon_memory.focus_phenomenon_id is not None and enaction.clock in self.workspace.memory.phenomenon_memory.phenomena[self.workspace.memory.phenomenon_memory.focus_phenomenon_id].position_pe:
            position_pe = round(self.workspace.memory.phenomenon_memory.phenomena[self.workspace.memory.phenomenon_memory.focus_phenomenon_id].position_pe[enaction.clock])
            # Reduce serotonin if prediction error is low
            # if position_pe < 50:
            #     self.workspace.memory.body_memory.serotonin = max(40, self.workspace.memory.body_memory.serotonin - 1)

        if enaction.clock == 0:
            # Initialize the file with headers
            with open("log/00_Trace.csv", 'w', newline='') as file:
                csv.writer(file).writerow(["clock", "action", "predicted_outcome", "outcome_code", "pe_code", "floor",
                                           "pe_yaw", "re_yaw", "re_compass", "forward_pe", "position_pe", "serotonin"])
        # Append the enaction line
        with open("log/00_Trace.csv", 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([enaction.clock, enaction.command.action.action_code, enaction.predicted_outcome_code,
                             enaction.outcome_code, self.pe_outcome_code[enaction.clock], enaction.outcome.floor,
                             self.pe_yaw.get(enaction.clock, ""),
                             self.re_yaw.get(enaction.clock, ""), self.re_compass.get(enaction.clock, ""),
                             self.pe_speed_forward.get(enaction.clock, ""), position_pe,
                             self.workspace.memory.body_memory.serotonin])

    def plot(self):
        """Show the prediction error plots"""
        # The outcome code prediction error
        kwargs = {'bottom': -1, 'top': 2, 'fmt': 'sc', 'marker_size': 5}
        plot(self.pe_outcome_code, "Outcome code prediction error", "01_Outcome_code", "(0/1)", **kwargs)

        # The yaw prediction error cyan squares
        kwargs = {'bottom': -40, 'top': 40, 'fmt': 'sc', 'marker_size': 5}
        plot(self.pe_yaw, "Yaw prediction error", "02_yaw_pe", "(degree)", **kwargs)

        # Residual errors Yaw and Compass magenta squares
        kwargs = {'bottom': -20, 'top': 20, 'fmt': 'sm', 'marker_size': 5}
        plot(self.re_yaw, "Withdraw yaw residual error", "03_yaw_re", "(degree)", **kwargs)
        plot(self.re_compass, "Compass residual error", "04_Compass", "(degree)", **kwargs)

        # The speed as blue circles
        plot(self.x_speed, "X speed", "05_x_speed", "(mm/s)")
        plot(self.y_speed, "Y speed", "06_y_speed", "(mm/s)")
        # plot(self.value_speed_forward, "Forward speed value", "Forward_speed_value", "(mm/s)")
        # plot(self.value_speed_backward, "Backward speed value", "Backward_speed_value", "(mm/s)")

        # The translation duration prediction errors in seconds as red squares
        kwargs = {'bottom': -1, 'top': 1, 'fmt': 'sr', 'marker_size': 5}
        plot(self.pe_forward_duration1, "Forward duration prediction error", "07_Forward_duration_pe", "(s)", **kwargs)
        plot(self.pe_lateral_duration1, "Swipe duration prediction error", "08_Swipe_duration_pe", "(s)", **kwargs)

        # The prediction errors as red squares
        kwargs = {'bottom': -100, 'top': 100, 'fmt': 'sr', 'marker_size': 5}
        plot(self.pe_x_speed, "X speed prediction error", "09_x_speed_pe", "(mm/s)", **kwargs)
        plot(self.pe_y_speed, "Y speed prediction error", "10_y_speed_pe", "(mm/s)", **kwargs)
        # plot(self.pe_speed_forward, "Forward speed prediction error", "Forward_speed_pe", "(mm/s)", parameters)
        # plot(self.pe_speed_backward, "Backward speed prediction error", "Backward_speed_pe", "(mm/s)", parameters)
        plot(self.pe_echo_direction, "Head direction prediction error", "07_Head_direction", "(degree)", **kwargs)
        plot(self.pe_echo_distance, "Echo distance prediction error", "08_Echo_distance", "(mm)", **kwargs)

        # The focus as red squares
        kwargs = {'bottom': -100, 'top': 100, 'fmt': 'sr', 'marker_size': 5}
        plot(self.pe_focus_direction, "Focus direction prediction error", "11_Focus_direction", "(degree)", **kwargs)
        plot(self.pe_focus_distance, "Focus distance prediction error", "12_Focus_distance", "(mm)", **kwargs)

        terrain = self.workspace.memory.phenomenon_memory.terrain()
        if terrain is not None:
            plot(terrain.origin_prediction_error, "Terrain origin", "13_Origin", "(mm)")
