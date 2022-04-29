import json
import math
import random
import threading
import time
from tkinter import E
from ..Model.Agents import AgentRandom
from ..Model.Agents import AgentAlignNorth
from ..Model.Memories import MemoryV1
from ..Misc.WifiInterface import WifiInterface
from ..Misc.RobotDefine import *
from ..Views.EgocentricView import EgocentricView
import msvcrt
import pyglet

CONTROL_MODE_MANUAL = 0
CONTROL_MODE_AUTOMATIC = 1

class ControllerUserActionV2 :

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

    def __init__(self,  agent, memory, ip, view = None, synthesizer = None, hexa_memory = None, hexaview = None,automatic = True):
        # View
        self.view = view
        self.agent = agent
        self.memory = memory
        self.synthesizer = synthesizer
        self.hexa_memory = hexa_memory
        self.hexaview = hexaview
        self.azimuth = 0
        self.RETREAT_DISTANCE = RETREAT_DISTANCE
        self.automatic = automatic
        self.wifiInterface = WifiInterface(ip)
        self.outcome_bytes = b'{"status":"T"}'  # Default status T timeout

        self.outcome = 0
        self.enact_step = 0
        self.action = ""
        self.action_angle = 0
        emw = self.view if self.view is not None else None
        self.control_mode = CONTROL_MODE_MANUAL
        self.need_user_action = False #True if there a synthesizer and it has indecisive_cells
        self.user_action = None
        self.print_done = False
        self.need_traitement_flag= False
        self.cell_inde_a_traiter = None
        self.robot_command = None
        self.hexaview.extract_and_convert_interactions(self.hexa_memory)
        self.refresh_count = 0 # to reset hexaview some times
        if emw is not None:
            @emw.event
            def on_text(text):
                if text.upper() == "A":
                    self.control_mode = CONTROL_MODE_AUTOMATIC
                    print("Control mode: AUTOMATIC")
                elif text.upper() == "M":
                    self.control_mode = CONTROL_MODE_MANUAL
                    print("Control mode: MANUAL")

                if self.control_mode == CONTROL_MODE_MANUAL and not self.synthesizer.synthetizing_step == 1 and not self.need_traitement_flag :
                    
                    if self.enact_step == 0 and not self.need_user_action:
                        self.action_angle = emw.mouse_press_angle
                        #  if text == "/" or text == "+":  # Send the angle marked by the mouse click
                        #      text = json.dumps({'action': text, 'angle': emw.mouse_press_angle})
                        #self.command_robot(text)
                        self.robot_command = text
                    else:
                        message = "Waiting for previous outcome before sending new action" if self.enact_step != 0 else "Waiting for user action"
                        print(message)

        hemw = self.hexaview if self.hexaview is not None else None
        if hemw is not None:
            
            def on_text_hemw(text):
                if self.need_user_action :
                    if text.upper() == "Y":
                        self.user_action = 'y',None
                        self.need_user_action = False
                    elif text.upper() == "N":
                        self.user_action = 'n',None
                        self.need_user_action = False
                else : 
                    if text.upper() == "A":
                        self.control_mode = CONTROL_MODE_AUTOMATIC
                        print("Control mode: AUTOMATIC")
                    elif text.upper() == "M":
                        self.control_mode = CONTROL_MODE_MANUAL
                        print("Control mode: MANUAL")

                    if self.control_mode == CONTROL_MODE_MANUAL and not self.synthesizer.synthetizing_step == 1 and not self.need_traitement_flag :
                    
                        if self.enact_step == 0 and not self.need_user_action:
                            self.action_angle = emw.mouse_press_angle
                            #  if text == "/" or text == "+":  # Send the angle marked by the mouse click
                            #      text = json.dumps({'action': text, 'angle': emw.mouse_press_angle})
                            #self.command_robot(text)
                            self.robot_command = text
                        else:
                            message = "Waiting for previous outcome before sending new action" if self.enact_step != 0 else "Waiting for user action"
                            print(message)
            hemw.on_text = on_text_hemw
            def on_mouse_press_hemw(x, y, button, modifiers):
                """ Computing the position of the mouse click in the hexagrid  """
                # Compute the position relative to the center in mm
                if self.need_user_action:
                    hexaview.mouse_press_x = int((x - hexaview.width/2)*hexaview.zoom_level*2)
                    hexaview.mouse_press_y = int((y - hexaview.height/2)*hexaview.zoom_level*2)
                    print(hexaview.mouse_press_x, hexaview.mouse_press_y)
                    cell_x, cell_y = self.hexa_memory.convert_pos_in_cell(hexaview.mouse_press_x, hexaview.mouse_press_y)
                    self.user_action = 'click',(cell_x,cell_y)
                    self.need_user_action = False
            hemw.on_mouse_press = on_mouse_press_hemw
            @hemw.event
            def on_mouse_motion(x, y, dx, dy):
                mouse_x = int((x - hemw.width/2)*hemw.zoom_level*2)
                mouse_y = int((y - hemw.height/2)*hemw.zoom_level*2)
                # Find the cell
                cell_x, cell_y = hexa_memory.convert_pos_in_cell(mouse_x, mouse_y)
                hemw.label.text = "Cell: " + str(cell_x) + ", " + str(cell_y)

    def main_loop(self,dt):
        """blabla"""
        if self.synthesizer.synthetizing_step == 1 and not self.need_traitement_flag :
            self.print_done = False
            self.cell_inde_a_traiter = self.synthesizer.indecisive_cells[-1]
            self.need_traitement_flag = True
            self.need_user_action = True
            self.user_action = None
        elif self.need_traitement_flag and self.user_action is not None :
            self.cell_inde_a_traiter = self.synthesizer.indecisive_cells[-1]
            self.synthesizer.apply_user_action(self.user_action)
            self.synthesizer.synthetize()
            self.need_traitement_flag = False
        elif not self.need_traitement_flag :
            #boucle normale
            robot_action = None
            if self.synthesizer.change_RETREAT_DISTANCE is not None :
                self.RETREAT_DISTANCE -= self.synthesizer.change_RETREAT_DISTANCE
                self.synthesizer.change_RETREAT_DISTANCE = None
                print("Changement retreat dist : ",self.RETREAT_DISTANCE)
            # 1 : demande l'action :
            if self.control_mode == CONTROL_MODE_AUTOMATIC :
                if(self.enact_step == 0):
                    self.automatic = True
                    self.action = self.ask_agent_for_action(self.outcome) # agent -> decider
                    robot_action = self.translate_agent_action_to_robot_command(self.action)
                # 2 : ordonne au robot
                    self.command_robot(robot_action)
            if self.robot_command is not None:
                    self.command_robot(self.robot_command)
                    self.robot_command = None
            if(self.enact_step >= 2):
                robot_data = self.outcome_bytes
                phenom_info, angle, translation, self.outcome, echo_array = self.translate_robot_data(robot_data)
                self.send_position_change_to_memory(angle,translation) #Might be an order problem between this line and the one under it, depending on
                self.send_position_change_to_hexa_memory(angle,translation)
                self.send_phenom_info_to_memory(phenom_info,echo_array) # when the robot detect interaction (before or after moving)
                self.memory.tick()
                self.enact_step = 0
                self.synthesizer.act()

    def main_refresh(self,dt):
        """Function that refresh the views"""
        if not self.need_traitement_flag :
            self.hexaview.indecisive_cell_shape = []
            self.hexaview.extract_and_convert_recently_changed_cells(self.hexa_memory)
            self.hexa_memory.cells_changed_recently = []
            self.view.extract_and_convert_interactions(self.memory)
            self.refresh_count += 1
            if self.refresh_count >= 5000 : # We keep adding shapes, so every once in a while we must clean everything to avoid memory shortages
                self.refresh_count = 0
                print("reset")
                self.hexaview.shapesList = []
                self.hexaview.extract_and_convert_interactions(self.hexa_memory)

        else :
            if not self.print_done :
                self.hexaview.show_indecisive_cell(self.cell_inde_a_traiter)
                self.print_done = True


    def mains(self,dt):
        self.main_refresh(dt)

        self.main_loop(dt)

        self.main_refresh(dt)
        
    def main(self):
        """Main function of the controller"""
        #pyglet.clock.schedule_interval(self.main_loop,0.5)
        #pyglet.clock.schedule_interval(self.main_refresh,0.1)
        pyglet.clock.schedule_interval(self.mains,0.1)
        pyglet.app.run()



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
    def send_phenom_info_to_memory(self,phenom_info,echo_array):
        """Send Interaction to the Memory
        """
        if self.memory is not None:
            self.memory.add(phenom_info)
            self.memory.add_echo_array(echo_array)

    def send_position_change_to_memory(self, angle, translation):
        """Send position changes (angle,distance) to the Memory
        """
        if self.memory is not None :
            self.memory.move(angle, translation)

    ################################################# HEXA_MEMORY RELATED #################################################################
    def send_position_change_to_hexa_memory(self,angle,translation):
        """Apply movement to hexamem"""
        if self.hexa_memory is not None:
            self.hexa_memory.azimuth = self.azimuth
            self.hexa_memory.move(angle,translation[0], translation[1])
            

    ################################################# ROBOT RELATED #################################################################

    def command_robot(self,action): #NOT TESTED
        """ Creating an asynchronous thread to send the action to the robot and to wait for outcome """
        self.outcome_bytes = "Waiting"
        def enact_thread():
            """ Sending the action to the robot and waiting for outcome """
            action_string = json.dumps({'action': self.action, 'angle': self.action_angle})
            print("Sending: " + action_string)
            self.outcome_bytes = self.wifiInterface.enact(action_string)
            print("Receive ", end="")
            print(self.outcome_bytes)
            self.enact_step = 2
            #print("Thread : enact_step = 2")
            # self.watch_outcome()

        self.action = action
        self.enact_step = 1
        thread = threading.Thread(target=enact_thread)
        thread.start()

        # Cas d'actions particulières :
        if action == "r":
            self.action_reset()

    ################################################# SPECIFIC TASKS #################################################################


    def action_reset(self):
        """Reset everything"""
        if self.hexa_memory is not None :
            self.hexa_memory.reset()

        if self.memory is not None :
            self.memory.reset()

        if self.synthesizer is not None :
            self.synthesizer.reset()

        return '0'

    def translate_agent_action_to_robot_command(self,action):
        """ Translate the agent action to robot commands
        """
        # 0-> '8', 1-> '1', 2-> '3', 3 -> 'tourne vers le nord'
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
        echo_array = []

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

            # Estimate displacement due to floor change retreat
            if floor > 0:  # Black line detected
                # Update the translation
                forward_duration = outcome['duration'] - 300  # Subtract retreat duration
                if self.action == "8":  # TODO Other actions
                    translation[0] = STEP_FORWARD_DISTANCE * forward_duration/1000 - self.RETREAT_DISTANCE
                    if (translation[0] < 0 ) :
                         print("translation negative")
                    if floor == 0b01:  # Black line on the right
                        translation[0] -= 0
                        translation[1] = RETREAT_DISTANCE_Y
                    if floor == 0b10:  # Black line on the left
                        translation[0] -= 0
                        translation[1] = -RETREAT_DISTANCE_Y
                if self.action == "4":
                    translation[0] = -self.RETREAT_DISTANCE
                    translation[1] = SHIFT_DISTANCE * forward_duration/1000
                if self.action == "6":
                    translation[0] = -self.RETREAT_DISTANCE
                    translation[1] = -SHIFT_DISTANCE * forward_duration/1000

                



            angle = rotation

            # Update head angle
            if 'head_angle' in outcome:
                head_angle = outcome['head_angle']
                if self.view is not None:
                    self.view.robot.rotate_head(head_angle)
                #  if self.action == "-" or self.action == "*" or self.action == "1" or self.action == "3" or self.action =="+":
                if self.action == "-" or self.action == "*" or self.action == "+":
                    print("Create a new echo interaction")
                    echo_distance = outcome['echo_distance']
                    if echo_distance > 0:  # echo measure 0 is false measure
                        if self.view is not None:
                            x = ROBOT_HEAD_X + math.cos(math.radians(head_angle)) * echo_distance
                            y = math.sin(math.radians(head_angle)) * echo_distance
                        obstacle = 1

            for i in range(100,-99,-10):
                    edstr = "ed"+str(i)

                    if edstr in outcome:
                        ha =i
                        ed = outcome[edstr]
                        tmp_x = ROBOT_HEAD_X + math.cos(math.radians(ha)) * ed
                        tmp_y = math.sin(math.radians(ha)) * ed
                        echo_array.append((tmp_x, tmp_y))
                        #print("ha :",ha,"ed :",ed, "tmp_x :",tmp_x,"tmp_y :",tmp_y)

            phenom_info = (floor,shock,blocked,obstacle,x,y)

        # Update the azimuth
        if 'azimuth' in outcome:
            self.azimuth = outcome['azimuth']
            #print("self az : ", self.azimuth)
        else:
            self.azimuth -= rotation

        angle = rotation
        return  phenom_info, angle, translation, outcome_for_agent,echo_array