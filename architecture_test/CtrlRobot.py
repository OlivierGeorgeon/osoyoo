from stage_titouan import *
import json
from stage_titouan.Misc.RobotDefine import *
import threading

class CtrlRobot():
    """Blabla"""

    def __init__(self,model,robot_ip):
        self.model = model

        self.wifiInterface = WifiInterface(robot_ip)
        self.points_of_interest = []
        self.action = ""
        self.enact_step = 0
        self.outcome_bytes = b'{"status":"T"}'  # Default status T timeout
        self.robot_has_started_acting = False
        self.robot_has_finished_acting = False
        self.robot_data = None

    def main(self,dt):
        """Blabla"""
        if self.enact_step == 2:
            print("action finie")
            self.robot_has_started_acting = False
            self.robot_has_finished_acting =True
            self.enact_step = 0
        if self.robot_has_finished_acting:
            self.robot_has_finished_acting = False
            self.robot_data = self.translate_robot_data(self.outcome_bytes)
            self.send_position_change_to_memory()
            self.send_position_change_to_hexa_memory()
            self.send_phenom_info_to_memory()
            self.model.f_memory_changed = True
            self.model.f_hexmem_changed = True
            self.model.f_new_things_in_memory = True
            print("memories updated")
        elif not self.robot_has_started_acting and self.model.f_agent_action_ready :
            self.model.f_agent_action_ready = False
            self.action = self.model.agent_action
            print("command_robot")
            self.command_robot(self.action)
            self.model.f_ready_for_next_loop = False
            self.robot_has_started_acting = True

        

    def send_phenom_info_to_memory(self):
        """Send Interaction to the Memory
        """
        phenom_info = self.robot_data['floor'],self.robot_data['shock'],self.robot_data['blocked'],self.robot_data['obstacle'],self.robot_data['x'],self.robot_data['y']
        echo_array = self.robot_data['echo_array']
        if self.model.memory is not None:
            self.model.memory.add(phenom_info)
            self.model.memory.add_echo_array(echo_array)        

    def send_position_change_to_memory(self):
        """Send position changes (angle,distance) to the Memory
        """
        if self.model.memory is not None :
            self.model.memory.move(self.robot_data['angle'], self.robot_data['translation'])

    def send_position_change_to_hexa_memory(self):
        """Apply movement to hexamem"""
        if self.model.hexa_memory is not None:
            self.model.hexa_memory.azimuth = self.robot_data['azimuth']
            print("CtrlRobot: send_position_change ",self.robot_data['angle'], self.robot_data['translation'][0], self.robot_data['translation'][1])
            self.model.hexa_memory.move(self.robot_data['angle'], self.robot_data['translation'][0], self.robot_data['translation'][1])

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
        print(outcome)
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
                print("translate robot data actyion 8888888888")
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
                    translation[0] = STEP_FORWARD_DISTANCE * forward_duration/1000 - RETREAT_DISTANCE
                    if (translation[0] < 0 ) :
                            print("translation negative")
                    if floor == 0b01:  # Black line on the right
                        translation[0] -= 0
                        translation[1] = RETREAT_DISTANCE_Y
                    if floor == 0b10:  # Black line on the left
                        translation[0] -= 0
                        translation[1] = -RETREAT_DISTANCE_Y
                if self.action == "4":
                    translation[0] = -RETREAT_DISTANCE
                    translation[1] = SHIFT_DISTANCE * forward_duration/1000
                if self.action == "6":
                    translation[0] = -RETREAT_DISTANCE
                    translation[1] = -SHIFT_DISTANCE * forward_duration/1000

                



            angle = rotation

            # Update head angle
            if 'head_angle' in outcome:
                head_angle = outcome['head_angle']
                if self.action == "-" or self.action == "*" or self.action == "+":
                    print("Create a new echo interaction")
                    echo_distance = outcome['echo_distance']
                    if echo_distance > 0:  # echo measure 0 is false measure
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

        azimuth = 0
        # Update the azimuth
        if 'azimuth' in outcome:
            azimuth = outcome['azimuth']
            #print("self az : ", self.azimuth)

        angle = rotation

        outcome = dict()
        outcome['translation'] = translation
        outcome['rotation'] = rotation
        outcome['angle'] = angle
        outcome['floor'] = floor
        outcome['shock'] = shock
        outcome['blocked'] = blocked
        outcome['obstacle'] = obstacle
        outcome['x'] = x
        outcome['y'] = y
        outcome['echo_array'] = echo_array
        outcome['azimuth'] = azimuth
        return  outcome





    def command_robot(self,action): #NOT TESTED
        """ Creating an asynchronous thread to send the action to the robot and to wait for outcome """
        self.outcome_bytes = "Waiting"
        def enact_thread():
            """ Sending the action to the robot and waiting for outcome """
            action_string = json.dumps({'action': self.model.agent_action, 'angle': self.model.action_angle})
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
            self.model.action_reset()