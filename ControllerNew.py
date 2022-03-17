import json
import math
import random
import threading
import time
from Agent5 import Agent5
from MemoryV1 import MemoryV1
from RobotDefine import *
from WifiInterface import WifiInterface
from OsoyooCar import OsoyooCar
from EgoMemoryWindowNew import EgoMemoryWindowNew
import msvcrt



#from Phenomenon import Phenomenon
#import time
import pyglet
#from pyrr import matrix44
#from Interaction import Interaction
#from MemoryNew import MemoryNew


class ControllerNew:
    """Controller of the application
    It is the only object in the application that should have access to every of the following objects :
    Robot, Agent, Memory, View

    It is responsible of the following tasks :
        -Translate Robot datas into Interaction, Outcomes, and position changes (angle, distance)
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
            - Send Interaction to the Memory
            - Send position changes (angle,distance) to the Memory

        View Related :
            - Ask the View to refresh itself after an action from the robot
            - Ask if the User has interacted with the view since the last iteration

        Robot Related :
            - Send Actions to the robot
            - Receive Datas from the robot
    """

    def __init__(self,  agent, memory, view = None, synthesizer = None, hexa_memory = None, hexaview = None,automatic = True):
        # View
        self.view = view
        self.agent = agent
        self.memory = memory
        self.synthesizer = synthesizer
        self.hexa_memory = hexa_memory
        self.hexaview = hexaview
        self.azimuth = 0

        self.automatic = automatic
        self.wifiInterface = WifiInterface()
        self.outcome_bytes = b'{"status":"T"}'  # Default status T timeout

        self.outcome = 0
        self.enact_step = 0
        self.action = ""
        # if self.view is not None:
        #    self.robot = OsoyooCar(self.view.batch)
        """    
        # Model
        
        self.phenomena = []
        self.robot = OsoyooCar(self.view.batch)

       
        
        self.outcome_bytes = b'{"status":"T"}'  # Default status T timeout
        """


    

    def main_loop(self,dt):
        """blabla"""
        robot_action = None
        # 1 : demande l'action :
        if(self.enact_step == 0):
            if self.automatic :
                self.action = self.ask_agent_for_action(self.outcome) # agent -> decider
                robot_action = self.translate_agent_action_to_robot_command(self.action)
                
            else :
                print("Input ?")
                robot_action = msvcrt.getch().decode("utf-8")
        # 2 : ordonne au robot
            self.command_robot(robot_action)
        if(self.enact_step >= 2):
            robot_data = self.outcome_bytes
            phenom_info, angle, translation, self.outcome = self.translate_robot_data(robot_data)
            self.send_position_change_to_memory(angle,translation) #Might be an order problem between this line and the one under it, depending on
            self.send_position_change_to_hexa_memory(angle,translation)
            self.send_phenom_info_to_memory(phenom_info) # when the robot detect interaction (before or after moving)
            self.ask_synthetizer_to_act()
            self.main_refresh()
            self.enact_step = 0

    def main_refresh(self):
        """Function that refresh the views"""
        if self.view is not None :
            self.view.extract_and_convert_phenomenons(self.memory)
        if self.hexaview is not None :
            self.hexaview.extract_and_convert_phenomenons(self.hexa_memory)
        


    def main(self):
        """Main function of the controller"""
        pyglet.clock.schedule_interval(self.main_loop,0.1)
        #pyglet.clock.schedule_interval(self.main_refresh,0.1)
        pyglet.app.run()
    ################################################# LOOP #################################################################"""

    
    ################################################# AGENT RELATED #################################################################
       

    def ask_agent_for_action(self,outcome):
        """ Ask for Action from the Agent 
            and Send Outcomes to the Agent
        """
        return self.agent.action(outcome)

    ################################################# SYNTHETIZER RELATED #################################################################

    def ask_synthetizer_to_act(self):
        if self.synthesizer is not None :
            self.synthesizer.act()

    ################################################# MEMORY RELATED #################################################################
    def send_phenom_info_to_memory(self,phenom_info):
        """Send Interaction to the Memory
        """
        if self.memory is not None:
            self.memory.add(phenom_info)

    def send_position_change_to_memory(self, angle, translation):
        """Send position changes (angle,distance) to the Memory
        """
        if self.memory is not None :
            self.memory.move(angle, translation)

    ################################################# HEXA_MEMORY RELATED #################################################################


    def send_position_change_to_hexa_memory(self,angle,translation):
        """Apply movement to hexamem"""
        if self.hexa_memory is not None:
            self.hexa_memory.move(angle,translation[0], translation[1])


    ################################################# ROBOT RELATED #################################################################

    def command_robot(self,action): #NOT TESTED
        """ Creating an asynchronous thread to send the action to the robot and to wait for outcome """
        self.outcome_bytes = "Waiting"
        def enact_thread():
            """ Sending the action to the robot and waiting for outcome """
            # print("Send " + self.action)
            self.outcome_bytes = self.wifiInterface.enact(self.action)
            print("Receive ", end="")
            print(self.outcome_bytes)
            self.enact_step = 2
            #print("Thread : enact_step = 2")
            # self.watch_outcome()

        self.action = action
        self.enact_step = 1
        thread = threading.Thread(target=enact_thread)
        thread.start()

        

        #data = self.outcome_bytes
        #return data


    ################################################# SPECIFIC TASKS #################################################################

    def translate_agent_action_to_robot_command(self,action):
        """ Translate the agent action to robot commands
        """
        # 0-> '8', 1-> '1', 2-> '3'
        commands = ['8', '1', '3']
        return commands[action]

    def translate_robot_data(self,data): #PAS FINITO ?
        """Translate data from the robot to data usable
        by the model
        """
        angle = 0
        outcome_for_agent = 0
        phenom_info = (0,0,0,0,None,None)
        translation = [0,0]
        rotation = 0
        obstacle = 0
        floor = 0
        shock = 0
        blocked = 0
        x = None
        y = None
        json_outcome = json.loads(self.outcome_bytes)

        # Updating the model from the latest received outcome
        outcome = json.loads(data)
        floor = 0
        if 'floor' in outcome:
            floor = outcome['floor']
            outcome_for_agent = json_outcome['floor']
        shock = 0
        if 'shock' in outcome and self.action == '8' and floor == 0:
            shock = outcome['shock']  # Yellow star
            outcome_for_agent = json_outcome['shock']
        blocked = 0
        if 'blocked' in outcome and self.action == '8' and floor == 0:
            blocked = outcome['blocked'] # Red star
            outcome_for_agent = json_outcome['shock'] #OULAH

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
                print("rotation :", rotation)

            # Estimate displacement due to floor change retreat
            if floor > 0:  # Black line detected
                # Update the translation
                if self.action == "8":  # TODO Other actions
                    forward_duration = outcome['duration'] - 300  # Subtract retreat duration
                    translation[0] = STEP_FORWARD_DISTANCE * forward_duration/1000 - RETREAT_DISTANCE  # To be adjusted
                    if (translation[0] < 0 ) :
                         print("translation negative") 
            angle = rotation

            # Update head angle
            if 'head_angle' in outcome:
                head_angle = outcome['head_angle']
                if self.view is not None:
                    self.view.robot.rotate_head(head_angle)
                if self.action == "-" or self.action == "*" or self.action == "1" or self.action == "3":
                    # Create a new echo phenomenon
                    echo_distance = outcome['echo_distance']
                    if echo_distance > 0 :  # echo measure 0 is false measure
                        if self.view is not None:
                            x = ROBOT_HEAD_X + math.cos(math.radians(head_angle)) * echo_distance
                            y = math.sin(math.radians(head_angle)) * echo_distance
                        obstacle = 1

            phenom_info = (floor,shock,blocked,obstacle,x,y)

        # Update the azimuth
        if 'azimuth' in outcome:
            self.azimuth = outcome['azimuth']
        else:
            self.azimuth -= rotation

        angle = rotation
        return  phenom_info, angle, translation, outcome_for_agent

    ################################################ DEPRECATED #####################################################
    def loop(self):# DEPRECATED #NOT IMPLEMENTED: Change of behavior when user interact with view
        #NOT IMPLEMENTED : MANUAL mode
        """ Main loop of the controller
            It has the responsibility to update all the system
            i.e. ask the decider for an action and apply all changes
            to the system
        """
        self.enact_step = 0
        self.action = self.ask_agent_for_action(self.outcome) # agent -> decider
        action_debug = self.action
        robot_action = self.translate_agent_action_to_robot_command(self.action)
        print("<CONTROLLER> action choisie par le robot = ", self.action)
        #time.sleep(1)
        self.command_robot(robot_action)


        while(self.enact_step < 2):   # refresh la vue tant que pas de reponses de command_robot 
            if self.view is not None:
                self.view.refresh(self.memory) # TODO: camerde
            if self.hexa_memory is not None :
                self.hexaview.refresh(self.hexa_memory)  # TODO: camerde
        self.enact_step = 0
        robot_data = self.outcome_bytes
        phenom_info, angle, translation, self.outcome = self.translate_robot_data(robot_data)
        self.send_position_change_to_memory(angle,translation) #Might be an order problem between this line and the one under it, depending on
        self.send_phenom_info_to_memory(phenom_info) # when the robot detect interaction (before or after moving)
        user_interaction = None
        if self.view is not None:
            user_interaction = self.ask_view_to_refresh_and_get_last_interaction_from_user(self.memory)
        self.memory.tick()

        if self.hexa_memory is not None :
             self.send_position_change_to_hexa_memory(angle,translation)
        if self.synthesizer is not None : 
            self.ask_synthetizer_to_act()
        if self.hexaview is not None :
            ""
            self.ask_hexaview_to_refresh(self.hexa_memory)
        return self.outcome,user_interaction
    
    def depr_send_position_change_to_hexa_memory(self,angle,translation):
        """Adapt position change to fit hexa_memory functioning
        angle is converted in nb of 60 degrees turns and translation is
        adapted to a number of radius
        """
        print("angle sent by controller: ", angle)
        self.hexa_memory.rotate_robot(-angle)
        distance = int(math.sqrt(translation[0]**2 + translation[1]**2 ) )
        print("translation = ", translation,
            " distance = ", distance)
        self.hexa_memory.go_forward(distance)

        ################################################# VIEW RELATED #################################################################
    def ask_view_to_refresh_and_get_last_interaction_from_user(self,memory):
        """ Ask the View to refresh itself after an action from the robot
            Ask if the User has interacted with the view since the last iteration
        """
        return self.view.refresh(memory)

    ################################################# HEXAVIEW RELATED #################################################################
    def ask_hexaview_to_refresh(self,hexamemory):
        """ Ask the hexaview to refresh after robot action and
        synthetizer work.
        """
        return self.hexaview.refresh(hexamemory)
if __name__ == '__main__':
    from Agent6 import Agent6
    from HexaMemory import HexaMemory
    from HexaView import HexaView
    from MemoryV1 import MemoryV1
    from EgoMemoryWindowNew import EgoMemoryWindowNew
    from Synthesizer import Synthesizer

    # Mandatory Initializations
    
    memory = MemoryV1()
    hexa_memory = HexaMemory(width = 40, height = 80,cells_radius = 10)
    agent = Agent6(memory, hexa_memory)
    # Optionals Initializations
    
    view = None
    view = EgoMemoryWindowNew()
    hexaview = None
    hexaview = HexaView()
    synthesizer = Synthesizer(memory,hexa_memory)
    automatic = False
    controller = ControllerNew(agent,memory,view = view, synthesizer = synthesizer,
         hexa_memory = hexa_memory, hexaview = hexaview,automatic = automatic)

    controller.main()


    