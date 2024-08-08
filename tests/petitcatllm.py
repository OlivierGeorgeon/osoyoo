#!/usr/bin/env python
##PRAGMAS
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=broad-exception-caught
# pylint: disable=redefined-outer-name
"""
PetitCatController Module for the PetitCat Project
This code currently written for Overview Documentation, Part III -- proof of concept of integrating an LLM framework (LangChain) with
the PetitCatController class and using this to control the simple Osoyoo robotic car embodiment.

(See documentation -- there are a number of Parts (i.e., volumes)  taking a user from the assembly of a simple PetitCat embodiment (the Osoyoo robotic car) all the way
to a full humanoid robotic embodiment interfaced to the Causal Cognitive Architecture with hybridization of an LLM module and von Neumann module.)

LLM API is added here to the PetitCatController class. Very straightforward code produces somewhat sophisticated behavior on the part of the robotic embodiment.
(User should have read Parts I and Part II of the Overview documentation -- you need the appropriate C/C++ code compiled by the Arduino IDE and running on your
robot's compatible microcontroller. This module discussed in Part III of the Overview documentation.)

This module provides a class to control the PetitCat robotic device, which by default is the robotic car.
The purpose is to ground your AI/AGI project in the real world by providing access to such embodiments.
The PetitCat project has a number of more advanced modules allowing, for example, active inference. This module,
however, is to provide the basics of providing your AI/AGI project with an embodiment.

Summary of Module: It allows sending motor commands and receiving sensory inputs to/from the robotic device like the previous PetitCatController 
class, which indeed is used again. However, an LLM of your choice via the LangChain framework now is sending motor commands and interpreting
sensory inputs autonomously.


"""

## IMPORTS
import socket
import json
import sys
import os
import re
from langchain_openai import OpenAI



## CONSTANTS
LLM_ERROR_MESSAGE = """
The key required for the currently used LLM is "openai_api_key" which
appears to read on your system as {key} which is unlikely to work.
You may need to obtain the LLM key for proper program functioning.
If the error occurs with a non-Windows OS please ensure "openai_api_key"
is being read appropriately by the Python coding or insert it into the code near this error message.
Please restart the program if function is not correct.
Note for Linux or macOS:
    export OPENAI_API_KEY="your_openai_api_key
    chmod +x agi01.py
"""
TOTAL_TRIALS = 20
TOTAL_LIMITED_TRIALS = 2
LLM_INITIAL_RESPONSE_PROMPT = 'What version of LLM are you? What is your name?'
TSP_INPUT_TEXT_TEMPLATE = (
    "Navigate a path to each city and back to the original city given these distances. "
    "Give the total distance (units are miles). Tell me how you solved this problem. Give the shortest path. {distances}")
COMPOSITIONALITY_INPUT_TEXT = (
    "there is a black sphere and to the right a black cube and to the right another black cube, "
    "and behind the middle black cube a white cylinder. "
    "If you place the black sphere on top of the black cube which is"
    "not near a cylinder then tell me what the scene looks like now.")
DISTANCES = [
    [0, 2451, 713, 1018, 1631, 1374, 2408, 213, 2571, 875, 1420, 2145, 1972],
    [2451, 0, 1745, 1524, 831, 1240, 959, 2596, 403, 1589, 1374, 357, 579],
    [713, 1745, 0, 355, 920, 803, 1737, 851, 1858, 262, 940, 1453, 1260],
    [1018, 1524, 355, 0, 700, 862, 1395, 1123, 1584, 466, 1056, 1280, 987],
    [1631, 831, 920, 700, 0, 663, 1021, 1769, 949, 796, 879, 586, 371],
    [1374, 1240, 803, 862, 663, 0, 1681, 1551, 1765, 547, 225, 887, 999],
    [2408, 959, 1737, 1395, 1021, 1681, 0, 2493, 678, 1724, 1891, 1114, 701],
    [213, 2596, 851, 1123, 1769, 1551, 2493, 0, 2699, 1038, 1605, 2300, 2099],
    [2571, 403, 1858, 1584, 949, 1765, 678, 2699, 0, 1744, 1645, 653, 600],
    [875, 1589, 262, 466, 796, 547, 1724, 1038, 1744, 0, 679, 1272, 1162],
    [1420, 1374, 940, 1056, 879, 225, 1891, 1605, 1645, 679, 0, 1017, 1200],
    [2145, 357, 1453, 1280, 586, 887, 1114, 2300, 653, 1272, 1017, 0, 504],
    [1972, 579, 1260, 987, 371, 999, 701, 2099, 600, 1162, 1200, 504, 0]]
SENSOR_DESCPN1 = (
    "A mobile robot gives the following sensor information: "
    "Motor Command Response: b'{clock:0,action:2,duration1:1001, head_angle:-80,echo_distance:272,floor:0,duration:1002,status:0}' "
    "This means its head turned (i.e., head_angle) 80 degrees counterclockwise and found an object at 272mm (i.e., echo_distance). "
    "The action value just repeats the driving command sent to it. "
    "The following action values are possible: '2' which means go backwards, '8' means go forward, '4' means go to the right, '6' means go to the left. "
    "In response to the sensor information, please give the robot an action command, i.e., the number 2, 4, 6, or 8.")
MOTOR_CODES = (
    "Based on the previous sensory information please now decide if you want the robotic car to go forwards, backwards, left,"
    "right or to even shuffle to the right or shuffle to the left. Make the best decision to avoid hitting any objects detected by ultrasound"
    "sensors. The following motor codes are possible: '1' means turn left, '2' which means go backwards, '3' means turn right"
    "'4' means shuffle to the right, '6' means shuffle to the left, '8' means go forwards. Please just output a single digit, nothing else. ")


## INITIALIZATIONS (incl Class PetitController)
def initialize_llm() -> OpenAI:
    """Initialize the LLM with the API key
    -Currently using OpenAI API but many other LLM API's
    can be used with the LangChain framework being used to abstract
    away the low-level features of various large language models
    -API password, i.e., key, is being stored as an environmental
    variable so it does not get reproduced with the source code
    """
    try:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key in (None, '', 0, ' '):
            print(LLM_ERROR_MESSAGE.format(key=openai_api_key))
            print('(Note: Code requires a subscribed API for using this OpenAI LLM')
            print('Program will terminate as a result since will not run otherwise. Please fix this issue.\n')
            sys.exit(1)
    except Exception as e:
        print(f'Error reading open_api_key: {e}')
        print(LLM_ERROR_MESSAGE.format(key=openai_api_key))
        print('Program will terminate as a result since will not run otherwise. Please fix this issue.\n')
        sys.exit(1)
    llm = OpenAI(api_key=openai_api_key) #type: ignore[arg-type]
    #mypy will indicate that the OpenAI class is expecting a "SecretStr" type
    # rather than read or cast as such, the mypy warning bypassed as variable
    # llm is only used locally
    #as can be seen by print statement below a typical value for variable "llm" may be:
    #  OpenAI Params: {'model_name': 'gpt-3.5-turbo-instruct', 'temperature': 0.7, 'top_p': 1,
    #  'frequency_penalty': 0, 'presence_penalty': 0, 'n': 1, 'logit_bias': {}, 'max_tokens': 256}
    print('\nThe features of the LLM API just initialized are:\n', llm, '\n')
    return llm


def test_llm_initial_response(llm, bypass=False) -> bool:
    """Test the initial response from LLM to see if it is working.
    -If bypass parameter is set, then this initial response is bypassed
    -Note that variable llm is required to use the LLM
    -Typical response below:
      I am an AI and do not have a version number. I do not have a name either, but you can call me OpenAI.
    """
    if bypass is True:
        return False
    print('\nInitial response from LLM to see if it is working:')
    response = llm.invoke(input=LLM_INITIAL_RESPONSE_PROMPT)
    print(response)
    print('\nInitial response end\n\n')
    return True


#START class PetitCatController
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
        action_string = json.dumps(command_dict) #converts dict to JSON string
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
#END class PetitCatController
##End initializations


##PROBLEMS AND ADDITIONAL PROMPTS FOR LLM
def solve_tsp_problem(llm) -> None:
    """Solve the TSP problem using the LLM.
    This is used for Alien AGI Simulation, i.e., not cog arch simulations.
    Note: Current size works with modest token size.
    No truncations or other issues were noted.
    Analysis reveals 202 tokens used, i.e., within 256 default limit.
    Increase tokens if larger inputs are used.
    TSP_INPUT_TEXT_TEMPLATE = (
    "Navigate a path to each city and back to the original city given these distances. "
    "Give the total distance (units are miles). Tell me how you solved this problem. Give the shortest path. {distances}")
    """
    for i in range(TOTAL_LIMITED_TRIALS):
        input_text = TSP_INPUT_TEXT_TEMPLATE.format(distances=DISTANCES) #prompt instruction plus distance matrix
        response = llm.invoke(input=input_text)
        print(f"\nTSP Problem: Run {i}: Response from OpenAI simulating Alien AGI:", response)


def solve_compositionality_problem(llm) -> None:
    """Solve the Compositionality problem using the LLM.
    This is used for Alien AGI Simulation, i.e., not cog arch simulations.
    COMPOSITIONALITY_INPUT_TEXT = (
    "there is a black sphere and to the right a black cube and to the right another black cube, "
    "and behind the middle black cube a white cylinder. "
    "If you place the black sphere on top of the black cube which is"
    "not near a cylinder then tell me what the scene looks like now.")
    """
    for i in range(TOTAL_LIMITED_TRIALS):
        response = llm.invoke(input=COMPOSITIONALITY_INPUT_TEXT) #see above for prompt contents
        print(f"\nCompositionality Problem: Run {i}: Response from OpenAI simulating Alien AGI:", response)

def extract_first_digit(input_string):
    '''Use to extract a digit representing a motor code from the
    LLM output
    '''
    match = re.search(r'\d', input_string)
    if match:
        return match.group()
    return None


##MAIN
def main():
    """initialize an instance of PetitCatController and define which
    code blocks to run
    -initialize_llm() will initialize the llm used and display its characteristics
    -test_llm_initial_response() then actually tries out
      the llm with a simple prompt asking what it is
    -code_blocks_to_run specifies which code to run since some of the runs can takes
      significant time and resources
    -then the various possible jobs for the llm can be specified
    -Can run various programs on called LLM


    """
    #initialize the LLM
    llm = initialize_llm()  #"llm" variable is needed for various llm operations in the other functions
    test_llm_initial_response(llm, bypass=False)

    #initialize the PetitCat robotics
    controller = PetitCatController()  #instance of this class for robot sensory and motor communication

    #decide which code blocks to run
    #code_blocks_to_run = ['tsp', 'compositionality', 'robotsense'] #use LLM with this code block
    code_blocks_to_run = ['robotsense'] #use LLM with this code block
    if not code_blocks_to_run:
        code_blocks_to_run = ['robotsense']  # update as needed
    print('\nThe LLM and the PetitCat controller have been successfully initialized.')
    print('(at this point unable to tell if Arduino code is running or not on the robotic embodiment but will see soon)')
    print(f'System note: codeblocks which will be run: {code_blocks_to_run}\n')

    #possible code blocks to run
    #pylint: disable=pointless-string-statement
    if 'tsp' in code_blocks_to_run:
        '''code block to demonstrate the travelling salesperson problem via LLM and PetitCat embodiment
        -pending integration with PetitCat
        '''
        print('\nPENDING integration with PetitCat whereby there is physical embodiment of the following problem and solution')
        solve_tsp_problem(llm)
    if 'compositionality' in code_blocks_to_run:
        '''code block to demonstrate a compositionality problem via LLM and PetitCat embodiment
        -pending integration with PetitCat
        '''
        print('\nPENDING integration with PetitCat whereby there is physical embodiment of the following problem and solution')
        solve_compositionality_problem(llm)
    if 'robotsense' in code_blocks_to_run:
        '''code block to demonstrate LLM controlling the PetitCat embodiment
        -currently uses the robotic car embodiment
        -currently tells robot to scan its environment and return ultrasonic readings
        -LLM analyzes the ultrasonic readings and in response provides a motor code
        -the motor code is executed by the PetitCat robotic car and then new ultrasonic
          readings are taken and sent to the LLM
        -above repeats until there is an exit code or the loop reaches its limit

        -pending better time-out control and 'try' construct of code for more robust operation
        -pending encapsulation into not only its own function/method but its own module
        -pending more instructive LLM prompts, although limited prompts used surprinsingly work adequately
        -purpose at this time largely as demonstration code
        '''
        for trial in range(TOTAL_TRIALS):  #2 at time of writing, TOTAL_TRIALS is 20 at time of writing
            print(f'\nrobotsense code block trial # {trial}\n')
            #scan envrt for ultrasonic readings
            motor_code = "-" #initial motor code to scan the ultrasonic sensors
            response = controller.motor_command(motor_code) #this response will have ultrasonic data
            print("ultrasonic sensory data:", response)
            if response is None:
                decoded_response = 'no_response'
            else:
                decoded_response = response.decode('utf-8') # decode the byte response to a string
            #feed envrt sensory scan to LLM to generate motor code
            instruction = "What do you make of this data from a mobile robot with an ultrasonic sensor: " + decoded_response
            print(llm.invoke(input=instruction))
            llmresponse = llm.invoke(input=MOTOR_CODES+" It is very important here to just output a single number and nothing else here.")
            print('\nllm motor code produced:', llmresponse)
            #now try out suggested motor code
            motor_code = extract_first_digit(llmresponse)
            print(f'\nmotor_code to be sent to the robotic car: {motor_code}')
            response = controller.motor_command(motor_code)
            print("\nMotor Command Response:", response)


    #end program
    print('\nDemonstration code to show LLM integrated with PetitCat Project is now over.')
    print('No data is being saved. No files to initialize. No return values.\n')


if __name__ == '__main__':
    #note that if petitcatllm.py is not run from command line then main() will not run, but can use
    #the various functions and classes of this module
    main()
