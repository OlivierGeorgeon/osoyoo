from this import d


class EchoObjectValidateds:
    """List of phenomena that have been validated"""

    def __init__(self, memory):
        self.phenomena = []
        self.memory = memory
        self.allocentric_memory = memory.allocentric_memory

    def try_and_add(self, experiences):
        """Try to find existing validated phenomena to link the echo experiences with
        Returns the experiences that have not been attributed to a phenomenon, and the average translation"""
        translation_x, translation_y = 0, 0
        sum_translation_x, sum_translation_y = 0, 0
        number_of_add = 0
        remaining_experiences = experiences
        for echo in experiences:
            for phenomenon in self.phenomena:
                position_matrix = echo.allocentric_position_matrix(
                    self.memory.body_memory.body_direction_matrix(),
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

    # def add_object(self, echo_object):
    #     """Add an phenomenon to the list of validated phenomena"""
    #     self.list_objects.append(echo_object)
    #
    # def add_objects(self, objects):
    #     """Add a list of phenomena to the list of validated phenomena"""
    #     self.list_objects.extend(objects)
