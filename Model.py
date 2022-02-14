class Model:

    def __init__(self, memory,decider,synthesizer,phenomenonCollection):
        self.memory = memory
        self.decider = decider
        self.synthesizer = synthesizer
        self.phenomenonCollection = phenomenonCollection

    def update_memory(self,angle, distance,interaction):
        