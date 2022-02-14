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
        super().tick()
        to_remove = []
        for p in self.phenomenons :
            if(p.durability >= 0):
                to_remove.append(p)
        self.phenomenons = [x for x in self.phenomenons if x not in to_remove]
