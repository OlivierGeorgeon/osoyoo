from ..Memory.EgocentricMemory.Experience import EXPERIENCE_LOCAL_ECHO, EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_ALIGNED_ECHO
from ..Memory.AllocentricMemory.GridCell import CELL_PHENOMENON
from .SynthesizerSubclasses.EchoObjectsToInvestigate import EchoObjectsToInvestigate


class Synthesizer:
    """Synthesizer"""
    def __init__(self, workspace):
        """Constructor"""
        self.workspace = workspace
        self.egocentric_memory = workspace.memory.egocentric_memory
        self.allocentric_memory = workspace.memory.allocentric_memory
        # self.internal_hexa_grid = AllocentricMemory(self.allocentric_memory.width, self.allocentric_memory.height)
        # self.interactions_list = []
        self.echo_objects_to_investigate = EchoObjectsToInvestigate(3, 3, self.workspace.memory, acceptable_delta=700)
        self.phenomena = []
        self.last_projection_for_context = []
        # self.experiences_central_echo = []
        self.last_used_id = 0
        self.last_action_had_focus = False
        self.last_action = None

    def integrate(self):
        """Create phenomena and update cells in allocentric memory"""

        # The experiences generated during this round
        experiences = [e for e in self.egocentric_memory.experiences if (e.id > self.last_used_id)]
        self.last_used_id = max([e.id for e in experiences], default=self.last_used_id)

        # Try to attach the echo experiences to validated phenomena and remove these experiences
        experiences_central_echo = [e for e in experiences if (e.type == EXPERIENCE_CENTRAL_ECHO or
                                                               e.type == EXPERIENCE_ALIGNED_ECHO)]
        experiences_central_echo, translation = self.try_and_add(experiences_central_echo)
        # Apply the correction of position relative to the phenomenon in focus
        self.apply_translation_to_hexa_memory(translation)

        # Try to attach the central echos to not yet validated phenomena and remove these central echos
        experiences_central_echo = self.echo_objects_to_investigate.try_and_add(experiences_central_echo)
        # Try to validate existing phenomena to investigate
        validated_phenomena = self.echo_objects_to_investigate.validate()
        # Add the validated phenomena to the list
        self.phenomena.extend(validated_phenomena)
        # Create new hypothetical phenomena from remaining central echo experiences
        self.echo_objects_to_investigate.create_hypothetical_phenomena(experiences_central_echo)

        # Create a new experience based on the aligned echo and tell if the focus was lost
        # focus_experiences, focus_lost = self.create_focus_echo()

        cells_changed = []
        action_to_return = None

        # # If the focus is kept
        # if not focus_lost:
        #     # Add the new aligned echo experience
        #     self.experiences_central_echo += focus_experiences
        #     # self.experiences_central_echo += experiences
        #     # Try to attach the central echos with existing phenomena and remove them
        #     self.experiences_central_echo, translation = self.try_and_add(self.experiences_central_echo)
        #     # Apply the correction of position relative to the phenomenon in focus
        #     self.apply_translation_to_hexa_memory(translation)
        #
        #     self.experiences_central_echo = self.echo_objects_to_investigate.try_and_add(self.experiences_central_echo)
        #     validated_phenomena = self.echo_objects_to_investigate.validate()
        #     # self.echo_objects_valided.add_objects(objects_validated)
        #     self.phenomena.extend(validated_phenomena)
        #     self.echo_objects_to_investigate.create_hypothetical_phenomena(self.experiences_central_echo)

        # Mark the new experiences in allocentric memory by changing the cell status
        self.apply_status_experience_to_cells([e for e in experiences if e.type != EXPERIENCE_LOCAL_ECHO])
        action_to_return = None
            # if self.echo_objects_to_investigate.need_more_sweeps():
            #     action_to_return = "-"  # The synthesizer need to scan again

        # Display focus cells OG 01/10/2022
        # cells_changed += self.synthesize([elem for elem in focus_experiences if elem.type == EXPERIENCE_FOCUS])

        # Display the validated phenomena in the grid
        self.apply_status_phenomena_to_cells()

        return action_to_return

    def apply_translation_to_hexa_memory(self, translation_between_echo_and_context):
        """Translate the robot in allocentric memory"""
        self.allocentric_memory.move(0, translation_between_echo_and_context, is_egocentric_translation=False)

    def apply_status_experience_to_cells(self, experiences):
        """Mark the experiences in the cells of allocentric Memory"""
        cells_treated = []
        for experience in experiences:
            x, y = experience.allocentric_from_matrices(self.workspace.memory.body_memory.body_direction_matrix(),
                                                        self.allocentric_memory.body_position_matrix())
            cell_x, cell_y = self.allocentric_memory.convert_pos_in_cell(x, y)
            cells_treated.append((cell_x, cell_y))
            self.allocentric_memory.apply_status_to_cell(cell_x, cell_y, experience.type)
        return cells_treated

    def apply_status_phenomena_to_cells(self):
        """Mark the phenomena in the cells of allocentric memory"""
        for validated_phenomenon in self.phenomena:
            cell_i, cell_j = self.allocentric_memory.convert_pos_in_cell(validated_phenomenon.center[0],
                                                                         validated_phenomenon.center[1])
            self.allocentric_memory.apply_status_to_cell(cell_i, cell_j, CELL_PHENOMENON)

    # def create_focus_echo(self):
    #     """Create an aligned echo experience and tell if the focus was lost"""
    #     focus_lost = False
    #     if self.last_action_had_focus and self.workspace.enacted_interaction['echo_distance'] < 1000:  # OG
    #         distance = self.workspace.enacted_interaction['echo_distance']
    #         if distance > 800 and (self.last_action is not None) \
    #                 and not (self.last_action == "-" or self.last_action['action'] == "-"):
    #             focus_lost = True
    #         angle = self.workspace.enacted_interaction['head_angle']
    #         x = int(distance * math.cos(math.radians(angle)))
    #         y = int(distance * math.sin(math.radians(angle)))
    #         experience_focus = Experience(x, y, experience_type=EXPERIENCE_ALIGNED_ECHO, durability=5, decay_intensity=1,
    #                                       experience_id=self.egocentric_memory.experience_id)
    #         self.egocentric_memory.experience_id += 1
    #         return [experience_focus], focus_lost
    #     else:
    #         return [], focus_lost
    #
    def try_and_add(self, experiences):
        """Attach the experiences to existing phenomena if possible.
        Returns the experiences that have not been attached, and the average translation"""
        translation_x, translation_y = 0, 0
        sum_translation_x, sum_translation_y = 0, 0
        number_of_add = 0
        remaining_experiences = experiences.copy()
        for echo in experiences:
            for phenomenon in self.phenomena:
                position_matrix = echo.allocentric_position_matrix(
                    self.workspace.memory.body_memory.body_direction_matrix(),
                    self.allocentric_memory.body_position_matrix())
                is_added, translation = phenomenon.try_and_add(echo, position_matrix)
                if is_added:
                    sum_translation_x += translation[0]
                    sum_translation_y += translation[1]
                    number_of_add += 1
                    remaining_experiences.remove(echo)
                    break
        if number_of_add > 0:
            translation_x = sum_translation_x/number_of_add
            translation_y = sum_translation_y/number_of_add
        return remaining_experiences, (translation_x, translation_y)
