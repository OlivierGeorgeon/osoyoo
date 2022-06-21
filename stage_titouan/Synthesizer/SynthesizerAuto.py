from ..Memory.HexaMemory.HexaGrid import HexaGrid
from ..Misc.Utils import translate_interaction_type_to_cell_status
from ..Memory.EgocentricMemory.Interactions.Interaction import INTERACTION_ECHO
from ..Memory.HexaMemory.HexaGrid import HexaGrid
import numpy as np
from scipy.spatial.distance import cdist
import math
class SynthesizerAuto:
    """Synthesizer"""
    def __init__(self,memory,hexa_memory):
        """Constructor"""
        self.memory = memory
        self.hexa_memory = hexa_memory
        self.internal_hexa_grid = self.internal_hexa_grid = HexaGrid(hexa_memory.width, hexa_memory.height)
        self.interactions_list = []
        self.echo_objects_to_investigate = []
        self.echo_objects_valided = []

        self.last_real_echos = []

    def act(self):
        """blabla"""
        self.interactions_list = [elem for elem in self.memory.interactions if (elem.id>self.last_used_id)]
        if(len(self.interactions_list)<=0):
            return #TODOOO
        echoes = [elem for elem in self.interactions_list if elem.type == "Echo2"]
        real_echos = self.treat_echos(echoes)
        self.last_real_echos = real_echos
        

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