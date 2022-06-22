import numpy as np
import math
class EchoObject:
    """Blabla"""
    def __init__(self,echo_interaction, hexa_memory,acceptable_delta = 75):
        """Constructor
        Parameters:
            echo_interaction: the first echo interaction of the object phenomenon
            hexa_memory: the hexa memory used to convert egocentric coordinates to allocentric coordinates
            acceptable_delta: the acceptable delta between the allocentric coordinates of a new echo interaction and the center of the object phenomenon"""
        self.acceptable_delta = acceptable_delta
        self.echo_interactions = [echo_interaction]
        self.hexa_memory = hexa_memory
        self.allo_coordinates = [self.hexa_memory.convert_egocentric_position_to_allocentric(echo_interaction.x, echo_interaction.y)]
        self.center =self.hexa_memory.convert_pos_in_cell(self.allo_coordinates[0])
        self.has_been_validated = False
        
    def add_echo(self, echo_interaction):
        """Add an echo interaction to the object phenomenon, change the center to the mean of all the echo interactions allocentric coordinates"""
        self.echo_interactions.append(echo_interaction)
        allo_coordinates = self.hexa_memory.convert_egocentric_position_to_allocentric(echo_interaction.x, echo_interaction.y)
        self.allo_coordinates.append(allo_coordinates)

        if not self.has_been_validated:
            self.compute_center()

        
    def compute_center(self):
        """Compute the center of the object phenomenon"""
        self.center = np.mean(self.allo_coordinates,axis=0)

    def try_and_add(self,echo_interaction):
        """Test if the echo interaction is in the acceptable delta of the center of the object phenomenon, if yes, add it to the object phenomenon"""
        allocentric_coordinates = self.hexa_memory.convert_egocentric_position_to_allocentric(echo_interaction.x, echo_interaction.y)
        if math.dist(allocentric_coordinates-self.center)<self.acceptable_delta:
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