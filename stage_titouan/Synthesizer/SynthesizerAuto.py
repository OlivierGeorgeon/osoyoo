from ..Memory.HexaMemory.HexaGrid import HexaGrid
class SynthesizerAuto:
    
    def __init__(self,memory,hexa_memory):
        self.memory = memory
        self.hexa_memory = hexa_memory
        self.internal_hexa_grid = self.internal_hexa_grid = HexaGrid(hexa_memory.width, hexa_memory.height)
        