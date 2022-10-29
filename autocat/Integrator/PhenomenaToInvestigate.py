from autocat.Integrator.Phenomenon import Phenomenon


class PhenomenaToInvestigate:
    """List of phenomena to investigate"""
    def __init__(self, number_of_try_before_removing, number_of_echo_before_validation, memory):
        """Constructor
        Parameters:
            number_of_try_before_removing: the number of try before removing a phenomenon from the list
            number_of_echo_before_validation: the number of echo interactions needed to be added to an echo object to validate it"""
        self.list_objects_to_investigate = []
        self.validated_objects = []
        self.number_of_try_before_removing = number_of_try_before_removing
        self.number_of_echo_before_validation = number_of_echo_before_validation
        self.memory = memory
        self.allocentric_memory = memory.allocentric_memory

    def create_hypothetical_phenomena(self, experiences):
        """Create new phenomena to investigate from the list of central echos"""
        new_phenomena = []
        for experience in experiences:
            position_matrix = experience.allocentric_position_matrix(self.memory.body_memory.body_direction_matrix(),
                                                                     self.allocentric_memory.body_position_matrix())
            if len(new_phenomena) == 0:
                new_phenomena.append(Phenomenon(experience, position_matrix))
            else:
                clustered = False
                for new_phenomenon in new_phenomena:
                    # TODO compute the position matrix relative to the phenomenon position
                    if new_phenomenon.try_and_add(experience, position_matrix):
                        clustered = True
                        break
                    print("NOCLUSTO")
                if not clustered:
                    new_phenomena.append(Phenomenon(experience, position_matrix))
        for p in new_phenomena:
            print("New hypothetical phenomenon")
            self.list_objects_to_investigate.append([p, 0])

    def try_and_add(self, experiences):
        """Try to add the echo experiences to the phenomena to investigate"""
        remaining_experiences = experiences.copy()
        for experience in experiences:
            position_matrix = experience.allocentric_position_matrix(self.memory.body_memory.body_direction_matrix(),
                                                                     self.allocentric_memory.body_position_matrix())
            for phenomenon, _ in self.list_objects_to_investigate:
                print("A phenomenon is beeing investigated")
                if phenomenon.try_and_add(experience, position_matrix):
                    remaining_experiences.remove(experience)
                    break
        return remaining_experiences

    def validate(self):
        """Try to validate the objects to investigate
        Remove the objects that have been validated and 
        the objects that have been tried too much without meeting the
        threshold to be validated"""
        objet_validated = []
        for i, [objet, count] in enumerate(self.list_objects_to_investigate):
            objet.try_to_validate(self.number_of_echo_before_validation)
            if objet.has_been_validated:
                objet_validated.append(objet)
                self.list_objects_to_investigate.remove([objet, count])
            else:
                self.list_objects_to_investigate[i][1] += 1

        for objet in self.list_objects_to_investigate:
            if objet[1] > self.number_of_try_before_removing:
                self.list_objects_to_investigate.remove(objet)

        return objet_validated

    # def need_more_sweeps(self):
    #     """Return True if there are still objects to investigate"""
    #     return len(self.list_objects_to_investigate) > 0
