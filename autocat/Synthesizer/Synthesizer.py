from autocat.Memory.HexaMemory.Utils import translate_interaction_type_to_cell_status
# from ..Memory.EgocentricMemory.Interactions.Interaction import EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_FOCUS
from autocat.Memory.EgocentricMemory.Experience import *
from ..Memory.HexaMemory.HexaGrid import HexaGrid
import math
from .SynthesizerSubclasses.EchoObjectValidateds import EchoObjectValidateds
from .SynthesizerSubclasses.EchoObjectsToInvestigate import EchoObjectsToInvestigate


class Synthesizer:
    """Synthesizer
    (Involved in the focus)
    """
    def __init__(self, workspace):
        """Constructor"""
        self.workspace = workspace
        self.egocentric_memory = workspace.memory.egocentric_memory
        self.allocentric_memory = workspace.memory.allocentric_memory
        self.internal_hexa_grid = HexaGrid(self.allocentric_memory.width, self.allocentric_memory.height)
        self.interactions_list = []
        self.echo_objects_to_investigate = EchoObjectsToInvestigate(3, 2, self.allocentric_memory, acceptable_delta=700)
        self.echo_objects_valided = EchoObjectValidateds(self.allocentric_memory)
        self.last_projection_for_context = []
        self.experiences_central_echo = []
        self.last_used_id = 0
        self.last_action_had_focus = False
        self.last_action = None

    def act(self):
        """Handle everything the synthesizer has to do, from getting the last interactions in the memory
        to updating the hexa_memory"""
        self.interactions_list = [elem for elem in self.egocentric_memory.experiences if (elem.id > self.last_used_id)]
        self.last_used_id = max([elem.id for elem in self.interactions_list], default=self.last_used_id)
        echoes = [elem for elem in self.interactions_list if elem.type == EXPERIENCE_LOCAL_ECHO]
        real_echos = self.treat_echos(echoes)
        self.experiences_central_echo = real_echos
        echo_focus, focus_lost = self.create_focus_echo()
        cells_changed = []
        action_to_return = None
        if not focus_lost:
            real_echos += echo_focus
            real_echos, translation = self.echo_objects_valided.try_and_add(real_echos)
            self.apply_translation_to_hexa_memory(translation)
            real_echos = self.echo_objects_to_investigate.try_and_add(real_echos)
            objects_validated = self.echo_objects_to_investigate.validate()
            self.echo_objects_valided.add_objects(objects_validated)
            self.echo_objects_to_investigate.create_news(real_echos)
            cells_changed = self.synthesize([elem for elem in self.interactions_list if elem.type != "Echo" and elem.type != EXPERIENCE_LOCAL_ECHO])
            action_to_return = None
            if self.echo_objects_to_investigate.need_more_sweeps():
                action_to_return = "-"  # The synthesizer need to scan again
        return action_to_return, cells_changed, focus_lost

    def treat_echos(self, echo_list):
        """In case of a sweep we obtain an array of echo, this function discretize 
        it to try to find the real position of the objects that sent back the echo
        
        To do so use 'strikes' which are series of consecutive echoes that are
        close enough to be considered as the same object, and consider that the
        real position of the object is at the middle of the strike"""
        if len(echo_list) == 1:
            print(echo_list[0])
        echo_list = self.revert_echoes_to_angle_distance(echo_list)
        max_delta_dist = 160
        max_delta_angle = math.radians(20)
        streaks = [[], [], [], [], [], [], [], [], [], [], [], []]
        angle_dist = [[], [], [], [], [], [], [], [], [], [], [], []]
        current_id = 0
        echo_list = sorted(echo_list, key=lambda elem: elem[0])  # on trie par angle, pour avoir les streak "préfaites"
        for angle, distance, interaction in echo_list:
            check = False
            for i, streak in enumerate(streaks):
                if len(streak)> 0 and not check:
                    if any((abs(ele[1]-distance)<max_delta_dist and abs(angle - ele[0])<max_delta_angle) for ele in streak):
                        streak.append((angle, distance, interaction))
                        angle_dist[i].append((math.degrees(angle), distance))
                        check = True
            if check:
                continue
            if len(streaks[current_id]) == 0:
                streaks[current_id].append((angle,distance,interaction))
                angle_dist[current_id].append((math.degrees(angle),distance))
            else :
                current_id = (current_id + 1)
                streaks[current_id].append((angle, distance, interaction))
                angle_dist[current_id].append((math.degrees(angle), distance))
        experiences_central_echo = []
        for streak in streaks:
            if len(streak) == 0:
                continue
            else:
                x_mean, y_mean = 0, 0
                if len(streak) % 2 == 0:
                    # Compute the means of x and y values for the two elements at the center of the array
                    x_mean = (streak[int(len(streak)/2)][2].x + streak[int(len(streak)/2)-1][2].x)/2
                    y_mean = (streak[int(len(streak)/2)][2].y + streak[int(len(streak)/2)-1][2].y)/2
                else:
                    # The x and y are at the center of the array
                    x_mean = streak[int(len(streak) / 2)][2].x
                    y_mean = streak[int(len(streak) / 2)][2].y
                experience_central_echo = Experience(int(x_mean), int(y_mean), width=15,
                                                     experience_type=EXPERIENCE_CENTRAL_ECHO, durability=5,
                                                     decay_intensity=1, experience_id=0)
                experiences_central_echo.append(experience_central_echo)
                self.egocentric_memory.experiences.append(experience_central_echo)  # OG add to memory for displacement update

        return experiences_central_echo

    def revert_echoes_to_angle_distance(self, echo_list):
        """Convert echo interaction to triples (angle,distance,interaction)"""
        output = []
        for elem in echo_list:
            # compute the angle using elem x and y
            angle = math.atan2(elem.y, elem.x)
            # compute the distance using elem x and y
            distance = math.sqrt(elem.x**2 + elem.y**2)
            output.append((angle, distance, elem))
        return output
    
    def apply_translation_to_hexa_memory(self, translation_between_echo_and_context):
        "Convert the egocentric translation given as parameter to an allocentric one, and apply it to the hexa_memory"
        allocentric_translation_x,allocentric_translation_y = translation_between_echo_and_context
        #print("Synthesizer correct position by",allocentric_translation_x,allocentric_translation_y)
        self.allocentric_memory.apply_translation_to_robot_pos(allocentric_translation_x, allocentric_translation_y)

    def synthesize(self, interactions_list):
        """Synthesize the interactions with the hexamem"""
        #Convert the interactions to an hexamem status and apply it to the
        #corresponding cells of the hexamem
        cells_treated = []
        for elem in interactions_list:
            #Convert the interaction 
            status = translate_interaction_type_to_cell_status(elem.type)
            #Apply the status to the hexamem
            allo_x, allo_y = self.get_allocentric_coordinates_of_interactions([elem])[0][0]
            cell_x, cell_y = self.allocentric_memory.convert_pos_in_cell(allo_x, allo_y)
            cells_treated.append((cell_x, cell_y))
            self.allocentric_memory.apply_status_to_cell(cell_x, cell_y, status)
        for object_valited in self.echo_objects_valided.list_objects :
            if not object_valited.printed :
                object_valited.printed = True
                x,y = object_valited.coord_x, object_valited.coord_y
                self.allocentric_memory.apply_status_to_cell(x, y, translate_interaction_type_to_cell_status("Echo"))
        return cells_treated

    def get_allocentric_coordinates_of_interactions(self, interaction_list):
        """ Compute allocentric coordinates for every interaction of the given type in self.interactions_list
        
        Return a list of ((x,y),interaction)"""
        rota_radian = math.radians(self.allocentric_memory.robot_angle)
        allocentric_coordinates = []
        for _, interaction in enumerate(interaction_list):
            corner_x, corner_y = interaction.x,interaction.y
            x_prime = int(corner_x * math.cos(rota_radian) - corner_y * math.sin(rota_radian) + self.allocentric_memory.robot_pos_x)
            y_prime = int(corner_y * math.cos(rota_radian) + corner_x * math.sin(rota_radian) + self.allocentric_memory.robot_pos_y)
            allocentric_coordinates.append(((x_prime,y_prime),interaction))
        return allocentric_coordinates

    def create_focus_echo(self):
        """Create a echo interaction corresponding to the focus"""
        focus_lost = False
        if self.last_action_had_focus:
            # distance = self.memory.last_enacted_interaction['echo_distance']  # OG 04/09/2022
            distance = self.workspace.enacted_interaction['echo_distance']
            if distance > 800 and (self.last_action is not None) and not (self.last_action == "-" or self.last_action['action'] == "-"):
                focus_lost = True
            # angle = self.memory.last_enacted_interaction['head_angle']
            angle = self.workspace.enacted_interaction['head_angle']  # OG 04/09/2022
            x = int(distance * math.cos(math.radians(angle)))
            y = int(distance * math.sin(math.radians(angle)))
            interaction_focus = Experience(x, y, width=15, experience_type=EXPERIENCE_FOCUS, durability=5, decay_intensity=1, experience_id=0)
            return [interaction_focus], focus_lost
        else:
            return [], focus_lost
