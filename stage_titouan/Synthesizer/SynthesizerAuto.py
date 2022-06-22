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

        self.last_real_echos = []

    def act(self):
        """blabla"""
        self.interactions_list = [elem for elem in self.memory.interactions if (elem.id>self.last_used_id)]
        if(len(self.interactions_list)<=0):
            return #TODOOO
        echoes = [elem for elem in self.interactions_list if elem.type == "Echo2"]
        real_echos = self.treat_echos(echoes)
        self.last_real_echos = real_echos

        real_echos,translation = self.echo_objects_valided.try_and_add(real_echos)
        self.apply_translation_to_hexa_memory(translation)
        real_echos = self.echo_objects_to_investigate.try_and_add(real_echos)
        objects_validated = self.echo_objects_to_investigate.validate()
        self.echo_objects_valided.add_objects(objects_validated)
        
        self.echo_objects_to_investigate.create_news(real_echos)

        self.synthesize([elem for elem in self.interactions_list if elem.type != "Echo" and elem.type != "Echo2"])
        action_to_return = None
        if(self.echo_objects_to_investigate.need_more_sweeps()):
            action_to_return = "sweep"
        return action_to_return

        

    def treat_echos(self, interactions_list):
        """Find true position of the objects echolocated"""
        #Filter self.interactions_list to keep only the echolocations (interaction.type == INTERACTION_ECHO)
        echo_list = [elem for elem in interactions_list if elem.type == INTERACTION_ECHO]
        #Compute distance between robot and echolocation for every element in echo_list
        dist_list = [math.sqrt(elem.x**2 + elem.y**2) for elem in echo_list]
        #Find all the local minimums in dist_list (dist_list[i] < dist_list[i+1] and dist_list[i] < dist_list[i-1])
        # append the corresponding echo to min_list
        min_list = [echo_list[i+1] for i,elem in enumerate(dist_list[1:-1]) if (elem<dist_list[i] and elem<=dist_list[i+2])]
        min_list = []
        min_ind_list = []
        for i,elem in enumerate(dist_list[1:-1]):
            if (elem<dist_list[i] and elem<dist_list[i+2]):
                #print("on va test")
                if( (len(min_ind_list )== 0) or (abs(min_ind_list[-1] - i+1) > 3 or abs(dist_list[min_ind_list[-1]-1] - elem) > 50 ) ):
                    #print("test ok")
                    min_list.append(echo_list[i+1])
                    min_ind_list.append(i+1)
        return min_list
    
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
        for elem in interactions_list:

            #Convert the interaction 
            status = translate_interaction_type_to_cell_status(elem.type)
            #Apply the status to the hexamem
            allo_x,allo_y = self.hexa_memory.convert_egocentric_coordinates_to_allocentric(elem.x,elem.y)
            cell_x, cell_y = self.hexa_memory.convert_allocentric_coordinates_to_cell(allo_x,allo_y)
            self.hexa_memory.apply_status_to_cell(cell_x, cell_y,status)