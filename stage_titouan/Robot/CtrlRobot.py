#from stage_titouan import *
import json
from stage_titouan.Robot.RobotDefine import *
from stage_titouan.Robot.WifiInterface import WifiInterface
import threading
from pyrr import matrix44
import math


class CtrlRobot():
    """Blabla"""

    def __init__(self,model,robot_ip):
        self.model = model

        self.wifiInterface = WifiInterface(robot_ip)

        # self.points_of_interest = []
        # self.action = ""

        self.intended_interaction = {'action': "8"}  # Need random initialization

        self.enact_step = 0
        self.outcome_bytes = b'{"status":"T"}'  # Default status T timeout

        self.robot_has_started_acting = False
        self.robot_has_finished_acting = False
        self.enacted_interaction = {}

    def main(self,dt):
        """Blabla"""
        if self.enact_step == 2:
            self.robot_has_started_acting = False
            self.robot_has_finished_acting =True
            self.enact_step = 0
        if self.robot_has_finished_acting:
            self.robot_has_finished_acting = False
            self.enacted_interaction = self.translate_robot_data()
            self.model.enacted_interaction = self.enacted_interaction
            if self.enacted_interaction["status"] != "T":
                self.send_position_change_to_memory()
                self.send_position_change_to_hexa_memory()
                self.send_phenom_info_to_memory()
                self.model.f_memory_changed = True
                self.model.f_hexmem_changed = True
                self.model.f_new_things_in_memory = True
        elif not self.robot_has_started_acting and self.model.f_agent_action_ready :
            self.model.f_reset_flag = False
            self.model.f_agent_action_ready = False
            #self.action = self.model.agent_action
            self.intended_interaction = self.model.intended_interaction
            self.command_robot(self.intended_interaction)
            self.model.f_ready_for_next_loop = False
            self.robot_has_started_acting = True

        

    def send_phenom_info_to_memory(self):
        """Send Interaction to the Memory
        """
        phenom_info = self.enacted_interaction['phenom_info']
        echo_array = self.enacted_interaction['echo_array']
        if self.model.memory is not None:
            self.model.memory.add(phenom_info)
            self.model.memory.add_echo_array(echo_array)        

    def send_position_change_to_memory(self):
        """Send position changes (angle,distance) to the Memory
        """
        if self.model.memory is not None :
            self.model.memory.move(self.enacted_interaction['yaw'], self.enacted_interaction['translation'])

    def send_position_change_to_hexa_memory(self):
        """Apply movement to hexamem"""
        if self.model.hexa_memory is not None:
            self.model.hexa_memory.azimuth = self.enacted_interaction['azimuth']
            self.model.hexa_memory.move(self.enacted_interaction['yaw'], self.enacted_interaction['translation'][0], self.enacted_interaction['translation'][1])

    def translate_robot_data(self): #PAS FINITO ?
        """ Computes the enacted interaction from the robot's outcome data """
        action = self.intended_interaction['action']
        enacted_interaction = json.loads(self.outcome_bytes)
        # enacted_interaction = {'action': action, 'status': outcome['status']}

        # If timeout then no ego memory update
        if enacted_interaction['status'] == "T":
            return enacted_interaction

        # Head angle
        # head_angle = 90
        # if 'head_angle' in outcome:
        #     head_angle = outcome['head_angle']
        # enacted_interaction['head_angle'] = head_angle

        # Presupposed displacement of the robot relative to the environment
        translation, yaw = [0, 0], 0
        if action == "1":
            yaw = 45
        if action == "2":
            translation[0] = -STEP_FORWARD_DISTANCE
        if action == "3":
            yaw = -45
        if action == "4":
            translation[1] = SHIFT_DISTANCE
        if action == "6":
            translation[1] = -SHIFT_DISTANCE
        if action == "8":
            translation[0] = STEP_FORWARD_DISTANCE # * outcome['duration'] / 1000

        # If the robot returns yaw then use it
        if 'yaw' in enacted_interaction:
            yaw = enacted_interaction['yaw']
        else:
            enacted_interaction['yaw'] = yaw

        # Compute the azimuth from compass_x and compass_y
        # You must set the offset such that compass_x is near 0 when the robot is East or West
        #                               and compass_y is near 0 when the robot is North or South.
        # see https://www.best-microcontroller-projects.com/hmc5883l.html
        if 'compass_x' in enacted_interaction:
            enacted_interaction['compass_x'] -= COMPASS_X_OFFSET
            enacted_interaction['compass_y'] -= COMPASS_Y_OFFSET
            self.azimuth = math.degrees(math.atan2(enacted_interaction['compass_y'], enacted_interaction['compass_x']))
            self.azimuth += 180;
            if self.azimuth >= 360:
                self.azimuth -= 360
            enacted_interaction['azimuth'] = int(self.azimuth)
            print("compass_x", enacted_interaction['compass_x'], "compass_y", enacted_interaction['compass_y'], "azimuth", int(self.azimuth))

        # If the robot does not return the azimuth then compute it from the yaw
        if 'azimuth' not in enacted_interaction:
            self.azimuth -= yaw
            enacted_interaction['azimuth'] = self.azimuth

        # interacting with phenomena
        obstacle, floor, shock, blocked, x, y = 0, 0, 0, 0, 0, 0
        echo_distance = 0

        if 'floor' in enacted_interaction:
            floor = enacted_interaction['floor']
        if 'shock' in enacted_interaction and action == '8' and floor == 0:
            shock = enacted_interaction['shock']
        if 'blocked' in enacted_interaction and action == '8' and floor == 0:
            blocked = enacted_interaction['blocked']
        if 'echo_distance' in enacted_interaction and action == "-" or action == "*" or action == "+":
            echo_distance = enacted_interaction['echo_distance']
            if 0 < echo_distance < 10000:
                obstacle = 1

        # Interaction trespassing
        if floor > 0:
            # The position of the interaction trespassing
            x, y = LINE_X, 0
            # The resulting translation
            forward_duration = enacted_interaction['duration']  # - 300  # Subtract retreat duration
            if action == "8":  # TODO Other actions
                translation[0] = STEP_FORWARD_DISTANCE * forward_duration / 1000 - RETREAT_DISTANCE
                if translation[0] < 0:
                    print("translation negative")
                if floor == 0b01:  # Black line on the right
                    translation[0] -= 0
                    translation[1] = RETREAT_DISTANCE_Y
                if floor == 0b10:  # Black line on the left
                    translation[0] -= 0
                    translation[1] = -RETREAT_DISTANCE_Y
            if action == "4":
                translation[0] = -RETREAT_DISTANCE
                translation[1] = SHIFT_DISTANCE * forward_duration / 1000
            if action == "6":
                translation[0] = -RETREAT_DISTANCE
                translation[1] = -SHIFT_DISTANCE * forward_duration / 1000

        # Interaction blocked
        if blocked:
            x, y = 110, 0

        # Interaction shock
        if shock == 0b01:
            x, y = 110, -80
        if shock == 0b11:
            x, y = 110, 0
        if shock == 0b10:
            x, y = 110, 80

        # Interaction ECHO
        if obstacle:
            x = int(ROBOT_HEAD_X + math.cos(math.radians(enacted_interaction['head_angle'])) * echo_distance)
            y = int(math.sin(math.radians(enacted_interaction['head_angle'])) * echo_distance)

        enacted_interaction['phenom_info'] = (floor, shock, blocked, obstacle, x, y)
        enacted_interaction['echo_distance'] = echo_distance

        # The displacement caused by this interaction
        enacted_interaction['translation'] = translation
        enacted_interaction['yaw'] = yaw
        translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
        rotation_matrix = matrix44.create_from_z_rotation(-math.radians(-enacted_interaction['yaw']))
        enacted_interaction['displacement_matrix'] = matrix44.multiply(rotation_matrix, translation_matrix)

        # Returning the enacted interaction
        # print("Enacted interaction:", enacted_interaction)
        enacted_interaction["echo_array"] = [] if not "echo_array" in enacted_interaction.keys() else enacted_interaction["echo_array"]
        return enacted_interaction

    def command_robot(self, intended_interaction):
        """ Creating an asynchronous thread to send the command to the robot and to wait for the outcome """
        self.outcome_bytes = "Waiting"

        def enact_thread():
            """ Sending the command to the robot and waiting for the outcome """
            action_string = json.dumps(self.intended_interaction)
            print("Sending: " + action_string)
            self.outcome_bytes = self.wifiInterface.enact(action_string)
            print("Receive: ", end="")
            print(self.outcome_bytes)
            self.enact_step = 2  # Now we have received the outcome from the robot

        # self.action = action
        self.intended_interaction = intended_interaction
        self.enact_step = 1  # Now we send the command to the robot for enaction
        thread = threading.Thread(target=enact_thread)
        thread.start()
        print(intended_interaction)
        # Cas d'actions particulières :
        if intended_interaction["action"] == "r":
            self.model.action_reset()