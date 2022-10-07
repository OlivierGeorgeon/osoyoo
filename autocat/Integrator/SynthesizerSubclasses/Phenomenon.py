import numpy as np
import math


class Phenomenon:
    """An hypothetical phenomenon"""
    def __init__(self, echo_interaction, memory, acceptable_delta=300):
        """Constructor
        Parameters:
            echo_interaction: the first echo interaction of the object phenomenon
            hexa_memory: the hexa memory used to convert egocentric coordinates to allocentric coordinates
            acceptable_delta: the acceptable delta between the allocentric coordinates of a new echo interaction and the center of the object phenomenon"""
        self.acceptable_delta = acceptable_delta
        self.echo_interactions = [echo_interaction]
        self.memory = memory
        self.hexa_memory = memory.allocentric_memory
        x, y = echo_interaction.get_allocentric_coordinates(self.memory.body_memory.body_direction_rad)
        x += self.hexa_memory.robot_pos_x
        y += self.hexa_memory.robot_pos_y
        self.allo_coordinates = [(x, y)]
        #print("aLLLLLOOOOO",self.allo_coordinates)
        #self.center =self.hexa_memory.convert_pos_in_cell(self.allo_coordinates[0][0], self.allo_coordinates[0][1])
        self.center = [x, y]
        self.has_been_validated = False
        self.printed = False
        self.coord_x = -1
        self.coord_y = -1
        
    def add_echo(self, experience):
        """Add an echo experience to the object phenomenon,
        change the center to the average of all the echo interactions allocentric coordinates"""
        self.echo_interactions.append(experience)
        # allo_coordinates = self.get_allocentric_coordinates_of_interactions([echo_interaction])[0][0]
        x, y = experience.get_allocentric_coordinates(self.memory.body_memory.body_direction_rad)
        x += self.hexa_memory.robot_pos_x
        y += self.hexa_memory.robot_pos_y
        self.allo_coordinates.append((x, y))

        if not self.has_been_validated:
            self.compute_center()

    def compute_center(self):
        """Compute the center of the object phenomenon"""
        sum_x = 0
        sum_y = 0
        i = 0
        #self.center = np.mean(self.allo_coordinates,axis=0)
        for allo_coord in self.allo_coordinates:
            sum_x += allo_coord[0]
            sum_y += allo_coord[1]
            i += 1
        self.center = (int(sum_x/i), int(sum_y/i))
        self.coord_x, self.coord_y = self.hexa_memory.convert_pos_in_cell(self.center[0], self.center[1])

    def try_and_add(self, experience):
        """Test if the echo interaction is in the acceptable delta of the center of the phenomenon,
        if yes, add it to the phenomenon"""
        # coord_tuple = self.get_allocentric_coordinates_of_interactions([echo_interaction])[0][0]
        x, y = experience.get_allocentric_coordinates(self.memory.body_memory.body_direction_rad)
        x += self.hexa_memory.robot_pos_x
        y += self.hexa_memory.robot_pos_y
        allocentric_coordinates = [x, y]
        ##print("DISTANCE TRY AND ADD : ", math.dist(allocentric_coordinates,self.center), "\n", "ALLO COORD :", allocentric_coordinates, "CENTER :", self.center)
        if math.dist(allocentric_coordinates, self.center) < self.acceptable_delta:
            dist_x = self.center[0]-allocentric_coordinates[0]
            dist_y = self.center[1]-allocentric_coordinates[1]
            self.add_echo(experience)
            return True, (dist_x, dist_y)
        else:
            return False, None

    def try_to_validate(self, number_of_echos_needed):
        """Try to validate the phenomenon, i.e. consider this phenomenon as valid.
        To do so, the number of echo interactions needed to be added must be reached"""
        if len(self.echo_interactions) >= number_of_echos_needed:
            self.has_been_validated = True
        return self.has_been_validated

    # def get_allocentric_coordinates_of_interactions(self,interaction_list):
    #     """ Compute allocentric coordinates for every interaction of the given type in self.interactions_list
    #     Return a list of ((x,y),interaction)"""
    #     rota_radian = self.memory.body_memory.body_direction_rad
    #     allocentric_coordinates = []
    #     for _, interaction in enumerate(interaction_list):
    #             corner_x,corner_y = interaction.x,interaction.y
    #             x_prime = int(corner_x* math.cos(rota_radian) - corner_y * math.sin(rota_radian) + self.hexa_memory.robot_pos_x)
    #             y_prime = int(corner_y * math.cos(rota_radian) + corner_x* math.sin(rota_radian) + self.hexa_memory.robot_pos_y)
    #             allocentric_coordinates.append(((x_prime,y_prime),interaction))
    #     return allocentric_coordinates