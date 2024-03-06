import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
from pyrr import Quaternion
from ..Decider.Action import ACTION_FORWARD, ACTION_BACKWARD
from ..Decider.Interaction import OUTCOME_LOST_FOCUS
from ..Utils import short_angle, point_to_head_direction_distance, assert_almost_equal_angles
from ..Integrator.OutcomeCode import CONFIDENCE_CONFIRMED_FOCUS

PREDICTION_ERROR_WINDOW = 100
RUNNING_AVERAGE_COEF = 0.25


def plot(data_dict, caption, file_name):
    """Plot the values in this dictionary"""
    point_x = list(data_dict.keys())
    point_y = list(data_dict.values())

    # Create the figure
    plt.figure(figsize=(6, 3))
    # Set plot properties
    plt.title(caption)
    plt.xlabel('Clock')
    plt.ylabel('Prediction error')
    plt.axhline(0, color='black', linewidth=0.5)
    # plt.axvline(0, color='black', linewidth=0.5)
    plt.grid(color='gray', linestyle='--', linewidth=0.5)
    # plt.legend()
    # plt.axis('equal')  # Ensure equal scaling of axes

    # The points
    plt.plot(point_x, point_y, marker='o', linestyle='-', color='b', label=None)

    # Show the plot
    # plt.ion()
    # plt.draw()
    # plt.show()
    # plt.pause(1)
    plt.savefig("log/" + file_name + ".pdf")
    plt.close()


class PredictionError:
    def __init__(self, workspace):
        """Initialize the prediction error arrays"""
        self.workspace = workspace
        self.pe_outcome_code = {}
        self.pe_forward_duration1 = {}  # (s)
        self.pe_yaw = {}  # (degree)
        self.pe_compass = {}  # (degree)
        self.pe_echo_direction = {}  # (degree)
        self.pe_echo_distance = {}  # (mm)
        self.pe_focus_direction = {}  # (degree)
        self.pe_focus_distance = {}  # (mm)
        self.pe_speed_forward = {}  # (mm/s)
        self.value_speed_forward = {}  # (mm/s)
        self.pe_speed_backward = {}  # (mm/s)
        self.value_speed_backward = {}  # (mm/s)

        self.previous_echo_distance = 0

    def log(self, enaction):
        """Compute the prediction errors: computed - actual"""
        computed_outcome = enaction.predicted_outcome
        actual_outcome = enaction.outcome

        # Outcome code
        pe = int(enaction.predicted_outcome_code != enaction.outcome_code)
        self.pe_outcome_code[enaction.clock] = pe
        self.pe_outcome_code.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
        print("Prediction Error Outcome Code", pe,
              "(predicted:", enaction.predicted_outcome_code, ", actual:", enaction.outcome_code, ")",
              "Average:", round(float(np.mean(list(self.pe_outcome_code.values())))),
              "std:", round(float(np.std(list(self.pe_outcome_code.values())))))

        # Translation FORWARD duration1

        if enaction.action.action_code in [ACTION_FORWARD] and actual_outcome.duration1 != 0:
            pe = (computed_outcome.duration1 - actual_outcome.duration1) / 1000  # / actual_outcome.duration1
            self.pe_forward_duration1[enaction.clock] = pe
            self.pe_forward_duration1.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
            print("Prediction Error Translate duration1 (simulation - measured)=", round(pe),
                  "Average:", round(float(np.mean(list(self.pe_forward_duration1.values()))), 2),
                  "std:", round(float(np.std(list(self.pe_forward_duration1.values())))), 2)

            # Forward speed

            self.value_speed_forward[enaction.clock] = self.workspace.actions[ACTION_FORWARD].translation_speed[0]
            if assert_almost_equal_angles(math.radians(actual_outcome.head_angle), 0, 11) and enaction.outcome_code != OUTCOME_LOST_FOCUS:
                action_speed = self.workspace.actions[ACTION_FORWARD].translation_speed[0]
                speed = (self.previous_echo_distance - actual_outcome.echo_distance) * 1000 / actual_outcome.duration1
                pe = round(action_speed - speed)
                self.pe_speed_forward[enaction.clock] = pe
                self.pe_speed_forward.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
                print("Prediction Error Speed (simulation", round(action_speed), " - measured", round(speed), ")=", pe,
                      "Average:", round(float(np.mean(list(self.pe_speed_forward.values()))), 1),
                      "std:", round(float(np.std(list(self.pe_speed_forward.values())))), 1)
                # Update the speed of the action
                self.workspace.actions[ACTION_FORWARD].translation_speed[0] = action_speed * (1. - RUNNING_AVERAGE_COEF) + speed * RUNNING_AVERAGE_COEF

        # self.previous_echo_distance = actual_outcome.echo_distance

        # Translation Backward

        if enaction.action.action_code in [ACTION_BACKWARD] and actual_outcome.duration1 != 0 and enaction.outcome_code != OUTCOME_LOST_FOCUS:
            self.value_speed_backward[enaction.clock] = self.workspace.actions[ACTION_BACKWARD].translation_speed[0]
            if assert_almost_equal_angles(math.radians(actual_outcome.head_angle), 0, 11):
                action_speed = self.workspace.actions[ACTION_BACKWARD].translation_speed[0]
                speed = (self.previous_echo_distance - actual_outcome.echo_distance) * 1000 / actual_outcome.duration1
                pe = round(action_speed - speed)
                self.pe_speed_backward[enaction.clock] = pe
                self.pe_speed_backward.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
                print("Prediction Error Speed Back (simulation", round(action_speed), " - measured", round(speed), ")=", pe,
                      "Average:", round(float(np.mean(list(self.pe_speed_backward.values()))), 1),
                      "std:", round(float(np.std(list(self.pe_speed_backward.values())))), 1)
                # Update the speed of the action
                self.workspace.actions[ACTION_BACKWARD].translation_speed[0] = action_speed * (1. - RUNNING_AVERAGE_COEF) + speed * RUNNING_AVERAGE_COEF

        self.previous_echo_distance = actual_outcome.echo_distance

        # yaw

        # pe = math.degrees(-short_angle(enaction.command.intended_yaw_quaternion, enaction.yaw_quaternion))
        pe = math.degrees(-short_angle(Quaternion.from_z_rotation(math.radians(computed_outcome.yaw)),
                                       enaction.trajectory.yaw_quaternion))
        self.pe_yaw[enaction.clock] = pe
        self.pe_yaw.pop(enaction.clock - PREDICTION_ERROR_WINDOW, None)
        print("Prediction Error Yaw (command - measure)=", round(pe, 1),
              "Average:", round(float(np.mean(list(self.pe_yaw.values()))), 1),
              "std:", round(float(np.std(list(self.pe_yaw.values()))), 1))

        # Compass prediction error

        self.pe_compass[enaction.clock] = math.degrees(enaction.trajectory.body_direction_delta)
        self.pe_compass.pop(actual_outcome.clock - PREDICTION_ERROR_WINDOW, None)
        print("Prediction Error Compass (integrated direction - compass measure)=",
              round(self.pe_compass[enaction.clock], 2), "Average:",
              round(float(np.mean(list(self.pe_compass.values()))), 2), "std:",
              round(float(np.std(list(self.pe_compass.values()))), 2))

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

    def plot(self):
        """Show the prediction error plots"""
        # The agg backend avoids interfering with pyglet windows
        # https://matplotlib.org/stable/users/explain/figure/backends.html
        matplotlib.use('agg')
        # Create the log directory if it does not exist because it is not included in git
        if not os.path.exists("log"):
            os.makedirs("log")
        # Generate the plots
        plot(self.pe_outcome_code, "Outcome code (0/1)", "Outcome_code")
        plot(self.pe_forward_duration1, "Forward duration (s)", "Forward_duration")
        plot(self.pe_speed_forward, "Forward speed (mm/s)", "Forward_speed_pe")
        plot(self.value_speed_forward, "Forward speed value (mm/s)", "Forward_speed_value")
        plot(self.pe_speed_backward, "Backward speed (mm/s)", "Backward_speed_pe")
        plot(self.value_speed_backward, "Backward speed value (mm/s)", "Backward_speed_value")
        plot(self.pe_yaw, "Yaw (degrees)", "yaw")
        plot(self.pe_compass, "Compass (degree)", "Compass")
        plot(self.pe_echo_direction, "Head direction (degree)", "Head_direction")
        plot(self.pe_echo_distance, "Echo distance (mm)", "Echo_distance")
        plot(self.pe_focus_direction, "Focus direction (degree)", "Focus_direction")
        plot(self.pe_focus_distance, "Focus distance (mm)", "Focus_distance")
        terrain = self.workspace.memory.phenomenon_memory.terrain()
        if terrain is not None:
            plot(terrain.origin_prediction_error, "Terrain origin (mm)", "Origin")


# Test plot
if __name__ == "__main__":
    test_dict = {0: 1, 1: 2, 2: 2, 3: 1, 4: 0}
    matplotlib.use('agg')
    plot(test_dict, "Test", "test")
