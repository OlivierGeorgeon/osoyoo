from this import d


class EchoObjectValidateds:
    """List of echoobject that had been validated"""

    def __init__(self,hexa_memory):
        self.list_objects = []
        self.hexa_mememory = hexa_memory

    def try_and_add(self,real_echos):
        """Try to find an existing validated object to link the echo with"""
        sum_translation_x,sum_translation_y = 0,0
        number_of_add = 0
        echo_restantes = real_echos
        for echo in real_echos:
            for objet in self.list_objects :
                boule,translation =  objet.try_and_add(echo)
                if boule:
                    sum_translation_x += translation[0]
                    sum_translation_y += translation[1]
                    number_of_add += 1
                    echo_restantes.remove(echo)
                    break
        translation_x = sum_translation_x/number_of_add
        translation_y = sum_translation_y/number_of_add
        return echo_restantes,(translation_x,translation_y)

    def add_object(self,echo_object):
        """Add an echo object to the list of validated objects"""
        self.list_objects.append(echo_object)

    def add_objects(self,objects):
        """Add a list of echo objects to the list of validated objects"""
        self.list_objects.extend(objects)