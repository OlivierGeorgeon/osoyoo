from this import d


class EchoObjectValidateds:
    """List of phenomena that have been validated"""

    def __init__(self, memory):
        self.list_objects = []
        self.memory = memory
        self.allocentric_memory = memory.allocentric_memory

    def try_and_add(self, real_echos):
        """Try to find an existing validated phenomenon to link the echo with"""
        sum_translation_x, sum_translation_y = 0, 0
        number_of_add = 0
        echo_restantes = real_echos
        for echo in real_echos:
            for objet in self.list_objects:
                position_matrix = echo.allocentric_position_matrix(
                    self.memory.body_memory.body_direction_matrix(),
                    self.allocentric_memory.body_position_matrix())
                boule, translation = objet.try_and_add(echo, position_matrix)
                if boule:
                    #print("BOULE CEST VALIDEEEE OUAI OUAI")
                    sum_translation_x += translation[0]
                    sum_translation_y += translation[1]
                    number_of_add += 1
                    echo_restantes.remove(echo)
                    break
        translation_x = sum_translation_x/number_of_add if number_of_add > 0 else 0
        translation_y = sum_translation_y/number_of_add if number_of_add > 0 else 0
        return echo_restantes, (translation_x, translation_y)

    # def add_object(self, echo_object):
    #     """Add an phenomenon to the list of validated phenomena"""
    #     self.list_objects.append(echo_object)
    #
    def add_objects(self, objects):
        """Add a list of phenomena to the list of validated phenomena"""
        self.list_objects.extend(objects)
