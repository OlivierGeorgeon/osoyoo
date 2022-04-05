# This resource is useful for Agent4
from Python.Agent.Resources import Interaction


class CompositeInteraction:
    composite_interaction_list = []

    def __init__(self, pre_interaction, post_interaction):
        self.pre_interaction = pre_interaction
        self.post_interaction = post_interaction
        self.weight = 1
        self.isActivated = False

    def increment_weight(self):
        self.weight += 1

    def __str__(self):
        """ Print interaction in the form <pre_interaction_post_interaction> """
        return "<" + self.pre_interaction.__str__() + self.post_interaction.__str__() + ">"

    def __hash__(self):
        """ The hash is necessary to use interactions as keys in a dictionary """
        return self.pre_interaction.__hash__()*100 + self.post_interaction.__hash__()

    def __eq__(self, other):
        """ Interactions are equal if they have the same pre and post interactions """
        if isinstance(other, self.__class__):
            return (self.pre_interaction == other.pre_interaction) and (self.post_interaction == other.post_interaction)
        else:
            return False

    @classmethod
    def create_or_retrieve(cls, pre_interaction, post_interaction):
        interaction = CompositeInteraction(pre_interaction, post_interaction)

        if interaction in cls.composite_interaction_list:
            i = cls.composite_interaction_list.index(interaction)
            # print("Retrieving ", end="")
            # print(cls.interaction_list[i])
            return cls.composite_interaction_list[i]
        else:
            # print("Creating ", end="")
            # print(interaction)
            cls.composite_interaction_list.append(interaction)
            return interaction


if __name__ == '__main__':
    """ demonstrate the usage of CompositeInteraction.create_or_retrieve() """
    interaction00 = Interaction.create_or_retrieve(0, 0)  # Create
    interaction01 = Interaction.create_or_retrieve(0, 1)  # Create
    interaction10 = Interaction.create_or_retrieve(1, 0)  # Create
    interaction11 = Interaction.create_or_retrieve(1, 1)  # Create
    interaction00 = Interaction.create_or_retrieve(0, 0)  # Retrieve

    interaction0000 = CompositeInteraction.create_or_retrieve(interaction00, interaction00)  # Create
    print(interaction0000)