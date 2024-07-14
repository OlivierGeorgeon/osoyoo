#!/usr/bin/env python
# pylint: disable=line-too-long,redefined-outer-name

"""
NOTE: THIS IS INCOMPLETE CODE QUICKLY WRITTEN IN 1/2 HOUR (however, it does work)
IT IS SIMPLY TO SHOW THE CONCEPT OF HAVING AN INTERFACE BETWEEN ONE'S AI/AGI PYTHON CODE AND A ROBOTIC EMBODIMENT
WORK PENDING

PetitCatController Module for the PetitCat Project

This module provides a class to control the PetitCat robotic device, which by default is the robotic car.
The purpose is to ground your AI/AGI project in the real world by providing access to such embodiments.
The PetitCat project has a number of more advanced modules allowing, for example, active inference. This module,
however, is to provide the basics of providing your AI/AGI project with an embodiment.

Summary of Module: It allows sending motor commands and receiving sensory inputs to/from the robotic device.

Nomenclature of saved files: petitcatN.py   e.g., petitcat2.py
This file will on its own allow your AI/AGI project access to a robotic device embodiment.

Example usage:
    # Run the program from the command line, optionally providing the IP address as a command-line argument:
    python petitcat2.py <robot_ip>

    # If no IP address is provided on the command line, the program will prompt the user with the updated message to input the IP address.
    You can find this IP address from the Arduino serial monitor after the USB cable is plugged into the device and Arduino
    code is downloaded (or already on the robotic device)
    (This IP address will be fetched automatically in future enhancements to the project.)

    # Example motor command
    motor_code = input("Enter motor command: ")
    response = controller.motor_command(motor_code)
    print("Motor Command Response:", response)

    # Example sensory input request
    sensory_system = input("Enter sensory system (ultrasound/ir): ")
    response = controller.sensory_input(sensory_system)
    print("Sensory Input Response:", response)
"""

import socket
import json
import sys

class PetitCatController:
    """
    A class to control the PetitCat robotic device.
    Summary of this class: It allows sending motor commands and receiving sensory inputs to/from the robotic device.

    Attributes:
        ip (str): The IP address of the robotic device.
        port (int): The port number for communication.
        timeout (int): The timeout for the socket in seconds.
        clock (int): The clock counter for actions.

    Nomenclature of saved files: petitcatN.py   e.g., petitcat2.py
    This file will on its own allow your AI/AGI project access to a robotic device embodiment.

    Methods:
        __init__(ip=None, port=8888, timeout=5): Initializes the PetitCatController.
        send_command(command_dict): Sends a command to the robotic device and receives the outcome.
        motor_command(motor_code): Sends a motor command to the robotic device.
        sensory_input(sensory_system): Requests sensory input from the robotic device.
    """

    def __init__(self, ip=None, port=8888, timeout=5):
        """
        Initializes the PetitCatController with the specified IP address, port, and timeout.

        If the IP address is not provided, it prompts the user to enter it or accepts it
        from the command line arguments.

        Nomenclature of saved files: petitcatN.py   e.g., petitcat2.py
        This file will on its own allow your AI/AGI project access to a robotic device embodiment.

        Args:
            ip (str, optional): The IP address of the robotic device. Defaults to None.
            port (int, optional): The port number for communication. Defaults to 8888.
            timeout (int, optional): The timeout for the socket in seconds. Defaults to 5.
        """
        if ip is None:
            if len(sys.argv) > 1:
                ip = sys.argv[1]
            else:
                ip = input("Please look at the Arduino Serial Monitor and tell me what IP address your robotic device is using: ")
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.timeout)
        self.clock = 0
        print(f"Connecting to robot at IP: {self.ip}")

    def send_command(self, command_dict):
        """
        Sends a command to the robotic device and receives the outcome.

        Nomenclature of saved files: petitcatN.py   e.g., petitcat2.py
        This file will on its own allow your AI/AGI project access to a robotic device embodiment.

        Args:
            command_dict (dict): The command dictionary to be sent.

        Returns:
            outcome (bytes): The outcome received from the robotic device, or None if there was an error.
        """
        action_string = json.dumps(command_dict)
        self.socket.sendto(bytes(action_string, 'utf-8'), (self.ip, self.port))
        try:
            outcome, _ = self.socket.recvfrom(512)
        except socket.error as error:
            print(f"Socket error: {error}")
            outcome = None
        return outcome

    def motor_command(self, motor_code):
        """
        Sends a motor command to the robotic device.

        Nomenclature of saved files: petitcatN.py   e.g., petitcat2.py
        This file will on its own allow your AI/AGI project access to a robotic device embodiment.

        Args:
            motor_code (str): The motor command to be sent.

        Returns:
            outcome (bytes): The outcome received from the robotic device, or None if there was an error.
        """
        command_dict = {'clock': self.clock, 'action': motor_code}
        outcome = self.send_command(command_dict)
        if outcome:
            self.clock += 1
        return outcome

    def sensory_input(self, sensory_system):
        """
        Requests sensory input from the robotic device.

        Nomenclature of saved files: petitcatN.py   e.g., petitcat2.py
        This file will on its own allow your AI/AGI project access to a robotic device embodiment.

        Args:
            sensory_system (str): The identifier of the sensory system (e.g., "ultrasound", "ir").

        Returns:
            outcome (bytes): The outcome received from the robotic device, or None if there was an error.
        """
        command_dict = {'clock': self.clock, 'action': 'sensory', 'system': sensory_system}
        outcome = self.send_command(command_dict)
        if outcome:
            self.clock += 1
        return outcome

# Small demo example
if __name__ == '__main__':
    controller = PetitCatController()
    print("\nDemo code. Incomplete code -- simply to try out the concept.")
    print("Enter 'exit' to exit the program.\n")

    while True:
        # Example motor command
        motor_code = input("Enter motor command: ")
        if motor_code == "exit":
            break
        response = controller.motor_command(motor_code)
        print("Motor Command Response:", response)

        # Example sensory input request
        sensory_system = input("Enter sensory system (ultrasound/ir): ")
        if sensory_system == "exit":
            break
        response = controller.sensory_input(sensory_system)
        print("Sensory Input Response:", response)
    print("\nThank you for trying out the demo. This is incomplete code that simply shows a concept for now.\n")
