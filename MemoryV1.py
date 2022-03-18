from MemoryNew import *
class MemoryV1(MemoryNew):
    """This version of the memory class aims to implement the concept
    of durability of the phenomenon in the memory.
    So our agent can forget about things he saw long ago.

    Author : TKnockaert
    """

    def __init__(self):
        super().__init__()

    def tick(self):
        """ Remove the interactions when they are too old """
        super().tick()
        to_remove = []
        for i in self.interactions:
            if i.actual_durability <= 0:
                to_remove.append(i)
        self.interactions = [x for x in self.interactions if x not in to_remove]
