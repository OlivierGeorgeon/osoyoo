import numpy
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_ALIGNED_ECHO
from .PhenomenaToInvestigate import PhenomenaToInvestigate
from .Affordance import Affordance
from .Phenomenon import Phenomenon

PHENOMENON_DELTA = 300


class Integrator:
    """The integrator creates the phenomena"""
    def __init__(self, workspace):
        """Constructor"""
        self.workspace = workspace
        self.egocentric_memory = workspace.memory.egocentric_memory
        self.allocentric_memory = workspace.memory.allocentric_memory
        self.body_memory = workspace.memory.body_memory
        # self.phenomena_to_investigate = PhenomenaToInvestigate(3, 3, self.workspace)
        self.phenomena = []
        self.last_projection_for_context = []
        self.last_used_id = 0

    def integrate(self):
        """Create phenomena and update cells in allocentric memory"""

        # The experiences generated during this round
        experiences = [e for e in self.egocentric_memory.experiences if (e.id > self.last_used_id)]
        self.last_used_id = max([e.id for e in experiences], default=self.last_used_id)
        # Keep only echo experiences (for now)
        experiences_central_echo = [e for e in experiences if (e.type == EXPERIENCE_CENTRAL_ECHO or
                                                               e.type == EXPERIENCE_ALIGNED_ECHO)]

        # Try to attach the echo experiences to existing phenomena and remove these experiences
        experiences_central_echo, position_correction = self.try_and_add(experiences_central_echo)

        # Adjust the robot's position in allocentric memory if any
        self.allocentric_memory.move(0, position_correction, is_egocentric_translation=False)

        # Try to attach the central echos to not yet validated phenomena and remove these central echos
        #    experiences_central_echo = self.phenomena_to_investigate.try_and_add(experiences_central_echo)
        # Try to validate existing phenomena to investigate
        #    validated_phenomena = self.phenomena_to_investigate.validate()
        # Add the validated phenomena to the list
        #    self.phenomena.extend(validated_phenomena)

        # Create new hypothetical phenomena from remaining central echo experiences
        # self.phenomena_to_investigate.create_hypothetical_phenomena(experiences_central_echo)
        self.create_hypothetical_phenomena(experiences_central_echo)

        # Mark the new experiences in allocentric memory by changing the cell status
        self.apply_status_experience_to_cells([e for e in experiences if e.type != EXPERIENCE_LOCAL_ECHO])

        # Display the validated phenomena in the grid
        self.attach_phenomena_to_cells()

        return None

    def apply_status_experience_to_cells(self, experiences):
        """Mark the experiences in the cells of allocentric Memory"""
        cells_treated = []
        for experience in experiences:
            point = experience.allocentric_from_matrices(self.workspace.memory.body_memory.body_direction_matrix(),
                                                         self.allocentric_memory.body_position_matrix())
            cell_x, cell_y = self.allocentric_memory.convert_pos_in_cell(point[0], point[1])
            cells_treated.append((cell_x, cell_y))
            self.allocentric_memory.apply_status_to_cell(cell_x, cell_y, experience.type)
        return cells_treated

    def attach_phenomena_to_cells(self):
        """Allocate the phenomena to the cells of allocentric memory"""
        for p in self.phenomena:
            cell_i, cell_j = self.allocentric_memory.convert_pos_in_cell(p.point[0], p.point[1])
            self.allocentric_memory.grid[cell_i][cell_j].allocate_phenomenon(p)

    def try_and_add(self, experiences):
        """Try to attach a list of central echos to phenomena  in the list .
        Returns the experiences that have not been attached, and the average translation"""
        translation_x, translation_y = 0, 0
        position_correction = numpy.array([0, 0, 0], dtype=numpy.int16)
        # sum_translation_x, sum_translation_y = 0, 0
        sum_translation = numpy.array([0, 0, 0], dtype=numpy.int16)
        number_of_add = 0
        remaining_experiences = experiences.copy()
        for echo in experiences:
            for phenomenon in self.phenomena:
                affordance_point = echo.allocentric_from_matrices(self.workspace.memory.body_memory.body_direction_matrix(),
                                                                  self.allocentric_memory.body_position_matrix())
                affordance = Affordance(affordance_point, echo)
                delta = phenomenon.try_and_add(affordance)
                if delta is not None:
                    # sum_translation_x += delta[0]
                    # sum_translation_y += delta[1]
                    sum_translation += delta
                    number_of_add += 1
                    remaining_experiences.remove(echo)
                    break
        if number_of_add > 0:
            # translation_x = sum_translation_x/number_of_add
            # translation_y = sum_translation_y/number_of_add
            position_correction = numpy.divide(sum_translation, number_of_add)
        return remaining_experiences, position_correction
        # return remaining_experiences, (translation_x, translation_y)

    def create_hypothetical_phenomena(self, experiences):
        """Create new phenomena from the list of experiences"""
        new_phenomena = []
        for experience in experiences:
            affordance_point = experience.allocentric_from_matrices(self.body_memory.body_direction_matrix(),
                                                                    self.allocentric_memory.body_position_matrix())
            affordance = Affordance(affordance_point, experience)
            if len(new_phenomena) == 0:
                new_phenomena.append(Phenomenon(affordance))
            else:
                clustered = False
                for new_phenomenon in new_phenomena:
                    if new_phenomenon.try_and_add(affordance) is not None:
                        clustered = True
                        break
                    print("NOCLUSTO")
                if not clustered:
                    new_phenomena.append(Phenomenon(affordance))

        self.phenomena.extend(new_phenomena)
