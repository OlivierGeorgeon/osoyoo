# Save this code as trace_letter_h.py

"""
This script uses the PetitCatController module to control a robotic device
to trace out the letter "H".
"""

import time
from petitcat2 import PetitCatController

def move_forward(ctrl, duration):
    """
    Move the robot forward for a specified duration.

    Args:
        ctrl (PetitCatController): The controller instance for the robot.
        duration (float): Time in seconds to move forward.
    """
    ctrl.motor_command("8")  # Assuming "8" is the command for moving forward
    time.sleep(duration)
    ctrl.motor_command("5")  # Assuming "5" is the command for stopping

def move_backward(ctrl, duration):
    """
    Move the robot backward for a specified duration.

    Args:
        ctrl (PetitCatController): The controller instance for the robot.
        duration (float): Time in seconds to move backward.
    """
    ctrl.motor_command("2")  # Assuming "2" is the command for moving backward
    time.sleep(duration)
    ctrl.motor_command("5")  # Assuming "5" is the command for stopping

def turn_left(ctrl, duration):
    """
    Turn the robot left for a specified duration.

    Args:
        ctrl (PetitCatController): The controller instance for the robot.
        duration (float): Time in seconds to turn left.
    """
    ctrl.motor_command("1")  # Assuming "1" is the command for turning left
    time.sleep(duration)
    ctrl.motor_command("5")  # Assuming "5" is the command for stopping

def turn_right(ctrl, duration):
    """
    Turn the robot right for a specified duration.

    Args:
        ctrl (PetitCatController): The controller instance for the robot.
        duration (float): Time in seconds to turn right.
    """
    ctrl.motor_command("3")  # Assuming "3" is the command for turning right
    time.sleep(duration)
    ctrl.motor_command("5")  # Assuming "5" is the command for stopping

def trace_h(ctrl):
    """
    Trace out the letter "H" with the robot.

    Args:
        ctrl (PetitCatController): The controller instance for the robot.
    """
    # Draw the left vertical line
    move_forward(ctrl, 2)
    move_backward(ctrl, 2)

    # Move to the middle
    turn_right(ctrl, 0.5)
    move_forward(ctrl, 1)
    turn_left(ctrl, 0.5)

    # Draw the horizontal line
    move_forward(ctrl, 1)
    move_backward(ctrl, 1)

    # Move to the right vertical line position
    turn_right(ctrl, 0.5)
    move_forward(ctrl, 1)
    turn_left(ctrl, 0.5)

    # Draw the right vertical line
    move_forward(ctrl, 2)
    move_backward(ctrl, 2)

if __name__ == '__main__':
    controller = PetitCatController()

    print("Tracing the letter 'H'")
    trace_h(controller)
    print("Finished tracing the letter 'H'")
