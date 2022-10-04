from ..Memory.EgocentricMemory.Experience import Experience, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_LOCAL_ECHO, \
    EXPERIENCE_FOCUS
# from ..Memory.AllocentricMemory.AllocentricMemory import AllocentricMemory
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
        # self.internal_hexa_grid = AllocentricMemory(self.allocentric_memory.width, self.allocentric_memory.height)
        # self.interactions_list = []
        self.echo_objects_to_investigate = EchoObjectsToInvestigate(3, 2, self.workspace.memory, acceptable_delta=700)
        self.echo_objects_valided = EchoObjectValidateds(self.allocentric_memory)
        self.last_projection_for_context = []
        self.experiences_central_echo = []
        self.last_used_id = 0
        self.last_action_had_focus = False
        self.last_action = None

    def act(self):
        """Handle everything the synthesizer has to do, from getting the last interactions in the memory
        to updating the hexa_memory"""
        experiences = [elem for elem in self.egocentric_memory.experiences if (elem.id > self.last_used_id)]
        self.last_used_id = max([elem.id for elem in experiences], default=self.last_used_id)

        focus_experiences, focus_lost = self.create_focus_echo()

        cells_changed = []
        action_to_return = None
        if not focus_lost:
            self.experiences_central_echo += focus_experiences
            self.experiences_central_echo, translation = self.echo_objects_valided.try_and_add(
                self.experiences_central_echo)
            self.apply_translation_to_hexa_memory(translation)
            self.experiences_central_echo = self.echo_objects_to_investigate.try_and_add(self.experiences_central_echo)
            objects_validated = self.echo_objects_to_investigate.validate()
            self.echo_objects_valided.add_objects(objects_validated)
            self.echo_objects_to_investigate.create_news(self.experiences_central_echo)
            cells_changed = self.synthesize([elem for elem in experiences
                                             if elem.type != EXPERIENCE_ALIGNED_ECHO
                                             and elem.type != EXPERIENCE_LOCAL_ECHO])
            action_to_return = None
            if self.echo_objects_to_investigate.need_more_sweeps():
                action_to_return = "-"  # The synthesizer need to scan again

        # TODO display line cells when focus lost
        # Display focus cells OG 01/10/2022
        print("Focus experience")  # TODO manage focus out of grid (when echo distance = 10000)
        cells_changed += self.synthesize([elem for elem in focus_experiences if elem.type == EXPERIENCE_FOCUS])

        return action_to_return, cells_changed

    def apply_translation_to_hexa_memory(self, translation_between_echo_and_context):
        """Translate the robot in allocentric memory"""
        # allocentric_translation_x,allocentric_translation_y = translation_between_echo_and_context
        # print("Synthesizer correct position by",allocentric_translation_x,allocentric_translation_y)
        # self.allocentric_memory.apply_translation_to_robot_pos(allocentric_translation_x, allocentric_translation_y)
        self.allocentric_memory.move(0, translation_between_echo_and_context, is_egocentric_translation=False)

    def synthesize(self, experiences):
        """Mark the interaction in the cells of allocentric Memory"""
        cells_treated = []
        for experience in experiences:
            # status = translate_interaction_type_to_cell_status(experience.type)
            # Apply the status to the hexamem
            # allo_x, allo_y = self.get_allocentric_coordinates_of_interactions([experience])[0][0]
            x, y = experience.get_allocentric_coordinates(self.workspace.memory.body_memory.body_direction_rad)
            x += self.allocentric_memory.robot_pos_x
            y += self.allocentric_memory.robot_pos_y
            # try:
            #     assert(abs(allo_x - x) <= 1 and abs(allo_y - y) <= 1)
            # except AssertionError:
            #     print("allo_x:", allo_x, "allo_y:", allo_y, "allo2_x:", x, "allo2_y:", y)
            #     exit()
            cell_x, cell_y = self.allocentric_memory.convert_pos_in_cell(x, y)
            cells_treated.append((cell_x, cell_y))
            self.allocentric_memory.apply_status_to_cell(cell_x, cell_y, experience.type)

        for object_valited in self.echo_objects_valided.list_objects:
            if not object_valited.printed:
                object_valited.printed = True
                x, y = object_valited.coord_x, object_valited.coord_y
                self.allocentric_memory.apply_status_to_cell(x, y, EXPERIENCE_ALIGNED_ECHO)
        return cells_treated

    def create_focus_echo(self):
        """Create focus experience"""
        focus_lost = False
        if self.last_action_had_focus:
            distance = self.workspace.enacted_interaction['echo_distance']
            if distance > 800 and (self.last_action is not None) \
                    and not (self.last_action == "-" or self.last_action['action'] == "-"):
                focus_lost = True
            angle = self.workspace.enacted_interaction['head_angle']
            x = int(distance * math.cos(math.radians(angle)))
            y = int(distance * math.sin(math.radians(angle)))
            experience_focus = Experience(x, y, experience_type=EXPERIENCE_FOCUS, durability=5, decay_intensity=1,
                                          experience_id=0)
            return [experience_focus], focus_lost
        else:
            return [], focus_lost
