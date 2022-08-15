from . EchoObject import  EchoObject
class EchoObjectsToInvestigate:
    """Echo objects to investigate"""
    def __init__(self,number_of_try_before_removing,number_of_echo_before_validation,hexa_memory,acceptable_delta):
        """Constructor
        Parameters:
            number_of_try_before_removing: the number of try before removing an echo object from the list of echo objects to investigate
            number_of_echo_before_validation: the number of echo interactions needed to be added to an echo object to validate it"""
        self.list_objects_to_investigate = []
        self.validated_objects = []
        self.number_of_try_before_removing = number_of_try_before_removing
        self.number_of_echo_before_validation = number_of_echo_before_validation
        self.hexa_memory = hexa_memory
        self.acceptable_delta = acceptable_delta

    def create_news(self,real_echos):
        """ blabla"""
        new_objets = []
        for echo in real_echos:
            if len(new_objets) == 0:
                new_objets.append(EchoObject(echo,self.hexa_memory,acceptable_delta=self.acceptable_delta))
            else :
                clustered = False
                for objet in new_objets:
                    if objet.try_and_add(echo):
                        clustered = True
                        break
    
                    print("NOCLUSTO")
                if not clustered:
                    new_objets.append(EchoObject(echo,self.hexa_memory,acceptable_delta=self.acceptable_delta))
        for objet in new_objets:
            #print("NEW OBJECTO")
            self.list_objects_to_investigate.append([objet,0])

    def try_and_add(self,real_echos):
        """Try to add the echo interactions to the objects to investigate"""
        echo_restantes = real_echos
        for echo in real_echos:
            for objet,_ in self.list_objects_to_investigate:
                print("kssssssssssssssssssssssssssssssssssss")
                if objet.try_and_add(echo) :
                    echo_restantes.remove(echo)
                    break
        return echo_restantes

    def validate(self):
        """Try to validate the objects to investigate
        Remove the objects that have been validated and 
        the objects that have been tried too much without meating the 
        threshold to be validated"""
        objet_validated = []
        for i, [objet,count] in enumerate(self.list_objects_to_investigate):
            objet.try_to_validate(self.number_of_echo_before_validation)
            if objet.has_been_validated:
                objet_validated.append(objet)
                self.list_objects_to_investigate.remove([objet,count])
            else :
                self.list_objects_to_investigate[i][1]+=1

        for objet in self.list_objects_to_investigate:
            if objet[1] > self.number_of_try_before_removing:
                self.list_objects_to_investigate.remove(objet)

        return objet_validated

    def need_more_sweeps(self):
        """Return True if there are still objects to investigate"""
        return len(self.list_objects_to_investigate) > 0