from ..Memory.HexaMemory.HexaGrid import HexaGrid
from ..Misc.Utils import translate_interaction_type_to_cell_status
from ..Memory.EgocentricMemory.Interactions.Interaction import INTERACTION_ECHO
from ..Memory.HexaMemory.HexaGrid import HexaGrid
import numpy as np
from scipy.spatial.distance import cdist
import math

from . SynthesizerSubclasses.EchoObject import EchoObject
from . SynthesizerSubclasses.EchoObjectValidateds import EchoObjectValidateds
from . SynthesizerSubclasses.EchoObjectsToInvestigate import EchoObjectsToInvestigate
class SynthesizerAuto:
    """Synthesizer"""
    def __init__(self,memory,hexa_memory):
        """Constructor"""
        self.memory = memory
        self.hexa_memory = hexa_memory
        self.internal_hexa_grid = self.internal_hexa_grid = HexaGrid(hexa_memory.width, hexa_memory.height)
        self.interactions_list = []
        self.echo_objects_to_investigate = EchoObjectsToInvestigate(3,2,self.hexa_memory,acceptable_delta = 75)
        self.echo_objects_valided = EchoObjectValidateds(hexa_memory)
        self.last_projection_for_context = []
        self.last_real_echos = []
        self.last_used_id = 0
        

    def act(self):
        """blabla"""
        print("BGNEGNGNGNGGNGN")
        self.interactions_list = [elem for elem in self.memory.interactions if (elem.id>self.last_used_id)]

        self.last_used_id = max([elem.id for elem in self.interactions_list],default = self.last_used_id)
        if(len(self.interactions_list)<=0):
            print("bah merdeeeee aloorrrr")
            return "-"
        echoes = [elem for elem in self.interactions_list if elem.type == "Echo2"]
        print("len echoes :",len(echoes))
        real_echos = self.treat_echos(echoes)
        self.last_real_echos = real_echos
        print("len real_echos at first",len(real_echos))

        real_echos,translation = self.echo_objects_valided.try_and_add(real_echos)
        print("len real_echos after objetc validatalitedd",len(real_echos))
        self.apply_translation_to_hexa_memory(translation)
        real_echos = self.echo_objects_to_investigate.try_and_add(real_echos)
        print("len real_echos after investiggg",len(real_echos))
        objects_validated = self.echo_objects_to_investigate.validate()
        self.echo_objects_valided.add_objects(objects_validated)
        
        self.echo_objects_to_investigate.create_news(real_echos)

        self.synthesize([elem for elem in self.interactions_list if elem.type != "Echo" and elem.type != "Echo2"])
        action_to_return = None
        if(self.echo_objects_to_investigate.need_more_sweeps()):
            action_to_return = "-"

        print("RETURN SYNTHEAOUT ACT :",action_to_return)
        return action_to_return

        

    def treat_echos(self,echo_list):
        """blabla"""
        if(len(echo_list) ==1):
            print(echo_list[0])
        echo_list = self.revert_echoes_to_angle_distance(echo_list)
        max_delta_dist = 130
        max_delta_angle = math.radians(20)
        streaks = [[],[],[],[],[],[],[],[],[],[],[],[]]
        angle_dist = [[],[],[],[],[],[],[],[],[],[],[],[]]
        current_id = 0
        echo_list = sorted(echo_list, key=lambda elem: elem[0]) # on trie par angle, pour avoir les streak "préfaites"
        for angle,distance,interaction in echo_list :
            check = False
            for i,streak in enumerate(streaks):
                if len(streak)> 0 and check == False:
                    if any((abs(ele[1]-distance)<max_delta_dist and abs(angle - ele[0])<max_delta_angle) for ele in streak):
                        streak.append((angle,distance,interaction))
                        angle_dist[i].append((math.degrees(angle),distance))
                        check = True
            if check:
                continue
            if (len(streaks[current_id]) == 0):
                streaks[current_id].append((angle,distance,interaction))
                angle_dist[current_id].append((math.degrees(angle),distance))
            else :
                current_id = (current_id + 1)
                streaks[current_id].append((angle,distance,interaction))
                angle_dist[current_id].append((math.degrees(angle),distance))
        output = []
        for streak in streaks :
            if len(streak) == 0 :
                continue
            else :
                output.append(streak[int(len(streak)/2)][2])
        return output
    def revert_echoes_to_angle_distance(self,echo_list):
        """blabla"""
        output = []
        for elem in echo_list:
            #compute the angle using elem x and y
            angle = math.atan2(elem.y,elem.x)
            #compute the distance using elem x and y
            distance = math.sqrt(elem.x**2 + elem.y**2)
            output.append((angle,distance,elem))
        return output
    
    def apply_translation_to_hexa_memory(self,translation_between_echo_and_context):
        "Convert the egocentric translation given as parameter to an allocentric one, and apply it to the hexa_memory"
        allocentric_translation_x,allocentric_translation_y = translation_between_echo_and_context
        #allocentric_translation_x,allocentric_translation_y = self.hexa_memory.convert_egocentric_translation_to_allocentric(translation_x,translation_y)
        print("SyntheContextV2 moves robot by",allocentric_translation_x,allocentric_translation_y)
        self.hexa_memory.apply_translation_to_robot_pos(allocentric_translation_x,allocentric_translation_y)


    def synthesize(self,interactions_list):
        """Synthesize the interactions with the hexamem"""
        #Convert the interactions to an hexamem status and apply it to the
        #corresponding cells of the hexamem
        cells_treated = []
        for elem in interactions_list:

            #Convert the interaction 
            status = translate_interaction_type_to_cell_status(elem.type)
            #Apply the status to the hexamem
            allo_x,allo_y = self.get_allocentric_coordinates_of_interactions([elem])[0][0]
            cell_x, cell_y = self.hexa_memory.convert_pos_in_cell(allo_x,allo_y)
            cells_treated.append((cell_x,cell_y))
            self.hexa_memory.apply_status_to_cell(cell_x, cell_y,status)


    def get_allocentric_coordinates_of_interactions(self,interaction_list):
        """ Compute allocentric coordinates for every interaction of the given type in self.interactions_list
        
        Return a list of ((x,y),interaction)"""
        rota_radian = math.radians(self.hexa_memory.robot_angle)
        allocentric_coordinates = []
        for _,interaction in enumerate(interaction_list):
                corner_x,corner_y = interaction.x,interaction.y
                x_prime = int(corner_x* math.cos(rota_radian) - corner_y * math.sin(rota_radian) + self.hexa_memory.robot_pos_x)
                y_prime = int(corner_y * math.cos(rota_radian) + corner_x* math.sin(rota_radian) + self.hexa_memory.robot_pos_y)
                allocentric_coordinates.append(((x_prime,y_prime),interaction))
        return allocentric_coordinates