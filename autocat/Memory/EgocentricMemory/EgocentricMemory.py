from autocat.Memory.EgocentricMemory.Experience import Experience
from autocat.Memory.EgocentricMemory.Experience import EXPERIENCE_LOCAL_ECHO

EXPERIENCE_PERSISTENCE = 5


class EgocentricMemory:
    """Stores and manages the egocentric memory"""

    def __init__(self):
        self.experiences = []
        self.experience_id = 0  # A unique ID for each experience in memory

    # def reset(self):
    #     self.experiences = []
    #     self.current_id = 0

    def update_and_add_experiences(self, enacted_interaction):
        """ Process the enacted interaction to update the egocentric memory
        - Move the previous experiences
        - Add new experiences
        """

        # Move the existing experiences
        for experience in self.experiences:
            experience.displace(enacted_interaction['displacement_matrix'])

        # Create new experiences from points in the enacted_interaction
        for p in enacted_interaction['points']:
            experience = Experience(p[1], p[2], 10, 10, experience_type=p[0], experience_id=self.experience_id,
                                    durability=EXPERIENCE_PERSISTENCE)
            self.experiences.append(experience)
            self.experience_id += 1

        # Create new experiences of type local_echo from echos in the echo_array
        if 'echo_array' in enacted_interaction:
            echo_array = enacted_interaction['echo_array']
            for _, echo in enumerate(echo_array):
                x = echo[0]
                y = echo[1]
                local_echo_experience = Experience(x, y, width=15, experience_type=EXPERIENCE_LOCAL_ECHO,
                                                   durability=EXPERIENCE_PERSISTENCE, decay_intensity=1,
                                                   experience_id=self.experience_id)
                self.experiences.append(local_echo_experience)
                self.experience_id += 1

        # Experiences of type central_echo are added by the synthesizer

    def tick(self):
        for e in self.experiences:
            e.tick()
        # Remove the experiences when they are too old
        to_remove = []
        for e in self.experiences:
            if e.actual_durability <= 0:
                to_remove.append(e)
        self.experiences = [x for x in self.experiences if x not in to_remove]

    # def empty(self):
    #     self.experiences.clear()

    # def last_action(self):
    #     return self.actions[-1] if len(self.actions) > 0 else None
