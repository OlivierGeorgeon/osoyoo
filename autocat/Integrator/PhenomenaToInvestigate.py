import numpy
from .Phenomenon import Phenomenon
from .Affordance import Affordance


class PhenomenaToInvestigate:
    """List of phenomena to investigate"""
    def __init__(self, number_of_try_before_removing, number_of_echo_before_validation, workspace):
        """Constructor
        Parameters:
            number_of_try_before_removing: the number of try before removing a phenomenon from the list
            number_of_echo_before_validation: the number of echo interactions needed to be added to an echo object to validate it"""
        self.phenomena_to_investigate = []
        self.validated_phenomena = []
        self.number_of_try_before_removing = number_of_try_before_removing
        self.number_of_echo_before_validation = number_of_echo_before_validation
        self.workspace = workspace
        self.memory = workspace.memory
        self.allocentric_memory = workspace.memory.allocentric_memory

    def create_hypothetical_phenomena(self, experiences):
        """Create new phenomena to investigate from the list of central echos"""
        new_phenomena = []
        for experience in experiences:
            # position_matrix = experience.allocentric_position_matrix(self.memory.body_memory.body_direction_matrix(),
            #                                                          self.allocentric_memory.body_position_matrix())
            affordance_point = experience.allocentric_from_matrices(self.memory.body_memory.body_direction_matrix(),
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
        for p in new_phenomena:
            print("New hypothetical phenomenon")
            self.phenomena_to_investigate.append([p, 0])

    def try_and_add(self, experiences):
        """Try to add the echo experiences to the phenomena to investigate"""
        remaining_experiences = experiences.copy()
        for experience in experiences:
            # position_matrix = experience.allocentric_position_matrix(self.memory.body_memory.body_direction_matrix(),
            #                                                          self.allocentric_memory.body_position_matrix())
            affordance_point = experience.allocentric_from_matrices(self.memory.body_memory.body_direction_matrix(),
                                                                    self.allocentric_memory.body_position_matrix())
            affordance = Affordance(affordance_point, experience)
            for phenomenon, _ in self.phenomena_to_investigate:
                print("A phenomenon is being investigated")
                if phenomenon.try_and_add(affordance) is not None:
                    remaining_experiences.remove(experience)
                    break
        return remaining_experiences

    def validate(self):
        """Try to validate the objects to investigate
        Remove the objects that have been validated and 
        the objects that have been tried too much without meeting the
        threshold to be validated"""
        objet_validated = []
        for i, [objet, count] in enumerate(self.phenomena_to_investigate):
            objet.try_to_validate(self.number_of_echo_before_validation)
            if objet.has_been_validated:
                objet_validated.append(objet)
                self.phenomena_to_investigate.remove([objet, count])
            else:
                self.phenomena_to_investigate[i][1] += 1

        for objet in self.phenomena_to_investigate:
            if objet[1] > self.number_of_try_before_removing:
                self.phenomena_to_investigate.remove(objet)

        return objet_validated

    # def need_more_sweeps(self):
    #     """Return True if there are still objects to investigate"""
    #     return len(self.list_objects_to_investigate) > 0
