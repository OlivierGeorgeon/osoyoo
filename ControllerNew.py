import json
from RobotDefine import *
import threading
from WifiInterface import WifiInterface
from Phenomenon import Phenomenon
import math
from OsoyooCar import OsoyooCar
from EgoMemoryWindow import EgoMemoryWindow
import pyglet
from pyrr import matrix44
from PhenomenonNew import *
from MemoryNew import *
from Agent5 import *



class ControllerNew:
    """Controller of the application
    It is the only object in the application that should have access to every of the following objects :
    Robot, Agent, Memory, View

    It is responsible of the following tasks :
        -Translate Robot datas into PhenomenonNew, Outcomes, and position changes (angle, distance)
        -Translate the Agent Actions into Robot Actions, and command the robot to execute them

    It has the following communications :
        VOCABULARY : for a class X wich the Y class (here Controller) communicate with : 
            Ask = X.ask(_) (a method of x is called, and x return a result)
            Send = X.receive(data) (a method of x is called, wich change the inner state of X)
            Receive = X does Y.receive(data)
            It is important to consider that both Ask and Send can be done by a single method
    
        Agent Related :
            - Ask for Action from the Agent 
            - Send Outcomes to the Agent

        Memory Related :
            - Send PhenomenonNew to the Memory
            - Send position changes (angle,distance) to the Memory

        View Related :
            - Ask the View to refresh itself after an action from the robot
            - Ask if the User has interacted with the view since the last iteration

        Robot Related :
            - Send Actions to the robot
            - Receive Datas from the robot
    """

    def __init__(self, view, agent, memory):
        # View
        self.view = view
        self.agent = agent
        self.memory = memory

        """    
        # Model
        self.wifiInterface = WifiInterface()
        self.phenomena = []
        self.robot = OsoyooCar(self.view.batch)

        self.action = ""
        self.enact_step = 0
        self.outcome_bytes = b'{"status":"T"}'  # Default status T timeout
        """


    

    
    ################################################# AGENT RELATED #################################################################
       

    def ask_agent_for_action(self,outcome):
        """ Ask for Action from the Agent 
            and Send Outcomes to the Agent
        """
        return self.agent.action(outcome)


    ################################################# MEMORY RELATED #################################################################
    def send_phenom_to_memory(self,phenom):
        """Send PhenomenonNew to the Memory
        """
        self.memory.add(phenom)

    def send_position_change_to_memory(self, angle, distance):
        """Send position changes (angle,distance) to the Memory
        """
        self.memory.move(angle, distance)

    ################################################# VIEW RELATED #################################################################
    def ask_view_to_refresh_and_get_last_interaction_from_user(self):
        """ Ask the View to refresh itself after an action from the robot
            Ask if the User has interacted with the view since the last iteration
        """
        return self.view.refresh()

    ################################################# ROBOT RELATED #################################################################

    def command_robot(self,action): #NOT IMPLEMENTED
        data = None
        return data


    ################################################# SPECIFIC TASKS #################################################################

    def translate_agent_action_to_robot_command(self,action): #NOT IMPLEMENTED
        command = None
        return command

    def translate_robot_data(self,data): #NOT IMPLEMENTED data = outcome_bytes ?
        phenom = None
        angle = None
        distance = None
        outcome_for_agent = None


        """ Updating the model from the latest received outcome """
        outcome = json.loads(data)
        floor = 0
        if 'floor' in outcome:
            floor = outcome['floor']
        shock = 0
        if 'shock' in outcome:
            shock = outcome['shock']
        blocked = False
        if 'blocked' in outcome:
            blocked = outcome['blocked']

        # floor_outcome = outcome['outcome']  # Agent5 uses floor_outcome

        if outcome['status'] == "T":  # If timeout no ego memory update
            print("No ego memory update")
        else:
            # Presupposed displacement of the robot relative to the environment
            translation = [0, 0]
            rotation = 0
            if self.action == "1":
                rotation = 45
            if self.action == "2":
                translation[0] = -STEP_FORWARD_DISTANCE
            if self.action == "3":
                rotation = -45
            if self.action == "4":
                translation[1] = SHIFT_DISTANCE
            if self.action == "6":
                translation[1] = -SHIFT_DISTANCE
            if self.action == "8":
                if not blocked:
                    translation[0] = STEP_FORWARD_DISTANCE * outcome['duration'] / 1000

            # Actual measured displacement if any
            if 'yaw' in outcome:
                rotation = outcome['yaw']

            # Estimate displacement due to floor change retreat
            if floor > 0:  # Black line detected
                # Update the translation
                if self.action == "8":  # TODO Other actions
                    forward_duration = outcome['duration'] - 300  # Subtract retreat duration
                    translation[0] = STEP_FORWARD_DISTANCE * forward_duration/1000 - RETREAT_DISTANCE  # To be adjusted
            angle = rotation
        return phenom, angle, translation, outcome_for_agent
    ################################################# LOOP #################################################################

    def loop(self, outcome):  # NOT IMPLEMENTED: Change of behavior when user interact with view
        self.action = self.ask_agent_for_action(outcome)
        robot_action = self.translate_agent_action_to_robot_command(self.action)
        robot_data = self.command_robot(robot_action)
        phenom, angle, distance, outcome = self.translate_robot_data(robot_data)
        self.send_position_change_to_memory(angle,distance)  # Might be an order problem between this line and the one under it, depending on
        self.send_phenom_to_memory(phenom)                  # when the robot detect phenomenon (before or after moving)
        interaction = self.ask_view_to_refresh_and_get_last_interaction_from_user()
        return outcome,interaction