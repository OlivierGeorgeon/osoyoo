import numpy as np
import math


class EchoObject:
    """Blabla"""
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
        self.allo_coordinates =  [self.get_allocentric_coordinates_of_interactions([echo_interaction])[0][0]]
        #print("aLLLLLOOOOO",self.allo_coordinates)
        #self.center =self.hexa_memory.convert_pos_in_cell(self.allo_coordinates[0][0], self.allo_coordinates[0][1])
        self.center = [self.allo_coordinates[0][0],self.allo_coordinates[0][1]]
        #print("CENTERRRRR", self.center)
        self.has_been_validated = False
        self.printed = False
        self.coord_x = -1
        self.coord_y = -1
        
    def add_echo(self, echo_interaction):
        """Add an echo interaction to the object phenomenon, change the center to the mean of all the echo interactions allocentric coordinates"""
        self.echo_interactions.append(echo_interaction)
        allo_coordinates = self.get_allocentric_coordinates_of_interactions([echo_interaction])[0][0]
        self.allo_coordinates.append(allo_coordinates)

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
        self.center = (int(sum_x/i),int(sum_y/i))
        self.coord_x, self.coord_y = self.hexa_memory.convert_pos_in_cell(self.center[0], self.center[1])


    def try_and_add(self,echo_interaction):
        """Test if the echo interaction is in the acceptable delta of the center of the object phenomenon, if yes, add it to the object phenomenon"""
        coord_tuple = self.get_allocentric_coordinates_of_interactions([echo_interaction])[0][0]
        allocentric_coordinates = [coord_tuple[0], coord_tuple[1] ]
        ##print("DISTANCE TRY AND ADD : ", math.dist(allocentric_coordinates,self.center), "\n", "ALLO COORD :", allocentric_coordinates, "CENTER :", self.center)
        if math.dist(allocentric_coordinates,self.center)<self.acceptable_delta:
            dist_x = self.center[0]-allocentric_coordinates[0]
            dist_y = self.center[1]-allocentric_coordinates[1]
            self.add_echo(echo_interaction)
            return True,(dist_x,dist_y)
        else:
            return False, None

    def validate(self):
        """Validate the object phenomenon, i.e. consider this object phenomenon as valid such that it can be used in the future
        and can be added to the hexa_memory"""
        self.has_been_validated = True

    def try_to_validate(self,number_of_echos_needed):
        """Try to validate the object phenomenon, i.e. consider this object phenomenon as valid such that it can be used in the future
        and can be added to the hexa_memory, to do so, the number of echo interactions needed to be added to the object phenomenon must be reached"""
        if len(self.echo_interactions)>=number_of_echos_needed:
            self.validate()
        return self.has_been_validated


    def get_allocentric_coordinates_of_interactions(self,interaction_list):
        """ Compute allocentric coordinates for every interaction of the given type in self.interactions_list
        
        Return a list of ((x,y),interaction)"""
        # rota_radian = math.radians(self.hexa_memory.robot_angle)
        rota_radian = self.memory.body_memory.body_direction_rad
        allocentric_coordinates = []
        for _,interaction in enumerate(interaction_list):
                corner_x,corner_y = interaction.x,interaction.y
                x_prime = int(corner_x* math.cos(rota_radian) - corner_y * math.sin(rota_radian) + self.hexa_memory.robot_pos_x)
                y_prime = int(corner_y * math.cos(rota_radian) + corner_x* math.sin(rota_radian) + self.hexa_memory.robot_pos_y)
                allocentric_coordinates.append(((x_prime,y_prime),interaction))
        return allocentric_coordinates