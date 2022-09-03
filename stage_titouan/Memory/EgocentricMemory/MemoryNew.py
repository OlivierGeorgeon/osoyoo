from . Interactions.Interaction import Interaction
from . Interactions.Interaction import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_LOCAL_ECHO, \
                                       EXPERIENCE_BLOCK, EXPERIENCE_SHOCK, EXPERIENCE_CENTRAL_ECHO, EXPERIENCE_FOCUS
from webcolors import name_to_rgb
import math
from pyrr import matrix44

INTERACTION_PERSISTENCE = 5


class MemoryNew:
    """This class play the role of a memory manager : it stocks Interaction objects,
    apply transformations to them (such as decay)
    and also as the responsibility to translate them to concrete shapes on the GUI.
    
    This aims to make both Interaction and the view modulables.

    Author: TKnockaert
    """

    def __init__(self):
        self.interactions = []
        self.current_id = 0
        self.last_enacted_interaction = None
        self.experiences_focus = []

    def reset(self):
        self.interactions = []
        self.current_id = 0

    def add_enacted_interaction(self, enacted_interaction):  # Added by Olivier 08/05/2022
        """ Construct the experiences and add them to memory from the enacted_interaction """
        self.last_enacted_interaction = enacted_interaction
        # Create experiences from points in the enacted_interaction
        for p in enacted_interaction['points']:
            interaction = Interaction(p[1], p[2], 10, 10, experience_type=p[0], experience_id=self.current_id,
                                      durability=INTERACTION_PERSISTENCE)
            self.interactions.append(interaction)
            self.current_id += 1

        # # Create experience from focus in enacted_interaction
        # if 'focus' in enacted_interaction:
        #     x = enacted_interaction['echo_xy'][0]
        #     y = enacted_interaction['echo_xy'][1]
        #     experience_focus = Interaction(x, y, 10, 10, experience_type=EXPERIENCE_FOCUS,
        #                                    experience_id=self.current_id, durability=2)
        #     self.interactions.append(experience_focus)
        #     self.current_id += 1
        #     print("CREATE EXPERIENCE FOCUS x=", x, ", y=", y)


    # def add(self, phenom_info):
    #     """Translate interactions information into an interaction object, and add it to the list
    #     Arg :
    #         phenom_info : (floor,shock,blocked)
    #     Author : TKnockaert
    #     """
    #     # x = 10
    #     # y = 10
    #     floor, shock, blocked, obstacle, x, y = phenom_info
    #     durability = INTERACTION_PERSISTENCE
    #
    #     if floor:
    #         floor_interaction = Interaction(30, 0, 10, 60, experience_type=EXPERIENCE_FLOOR,
    #                                         durability=durability, decay_intensity=1, experience_id=self.current_id)
    #         self.interactions.append(floor_interaction)
    #     if shock:
    #         shock_interaction = None
    #         if shock == 0b01:
    #             shock_interaction = Interaction(110, -80, 20, 60, experience_type=EXPERIENCE_SHOCK,
    #                                             durability=durability, decay_intensity=1, experience_id=self.current_id)
    #         if shock == 0b11:
    #             shock_interaction = Interaction(110, 0, 20, 60, experience_type=EXPERIENCE_SHOCK, durability=durability,
    #                                             decay_intensity=1, experience_id=self.current_id)
    #         else:
    #             shock_interaction = Interaction(110, 80, 20, 60, experience_type=EXPERIENCE_SHOCK, durability=durability,
    #                                             decay_intensity=1,  experience_id=self.current_id)
    #         self.interactions.append(shock_interaction)
    #     if blocked:
    #         block_interaction = Interaction(110, 0, 20, 60, experience_type=EXPERIENCE_BLOCK,
    #                                         durability=durability, decay_intensity=1, experience_id=self.current_id)
    #         self.interactions.append(block_interaction)
    #
    #     if obstacle:
    #         obstacle_interaction = Interaction(x, y, width=5, experience_type=EXPERIENCE_ALIGNED_ECHO,
    #                                            durability=durability, decay_intensity=1, experience_id=self.current_id)
    #         self.interactions.append(obstacle_interaction)
    #
    #     self.current_id += 1
        
    def add_echo_array(self, echo_array):
        """Convert echo array given as parameter to a list of interaction objects and add it to  self.interactions"""
        durability = INTERACTION_PERSISTENCE
        for _, echo in enumerate(echo_array):
            x = echo[0]
            #print("add_echo_array, x :",x)
            y = echo[1]
            local_echo_interaction = Interaction(x, y, width=15, experience_type=EXPERIENCE_LOCAL_ECHO,
                                                 durability=durability, decay_intensity=1, experience_id=self.current_id)
            self.interactions.append(local_echo_interaction)
            self.current_id += 1

    def tick(self):
        for p in self.interactions:
            p.tick()
        # Remove the interactions when they are too old
        to_remove = []
        for i in self.interactions:
            if i.actual_durability <= 0:
                to_remove.append(i)
        self.interactions = [x for x in self.interactions if x not in to_remove]

    def empty(self):
        self.interactions.clear()

    def move(self, rotation, translation):
        """ Compute the displacement matrix and apply it to the interactions """
        translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
        rotation_matrix = matrix44.create_from_z_rotation(math.radians(rotation))
        displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
        # Translate and rotate all the interactions
        for interaction in self.interactions:
            interaction.displace(displacement_matrix)

    # def add_action(self, action):
    #     self.actions.append(action)

    def last_action(self):
        return self.actions[-1] if len(self.actions)> 0 else None


# Test MemoryNew with CtrlView:
# py -m stage_titouan.Display.EgocentricDisplay.CtrlView
