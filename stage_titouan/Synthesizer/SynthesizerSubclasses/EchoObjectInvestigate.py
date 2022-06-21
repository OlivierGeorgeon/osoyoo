class EchoObjectInvestigate:
    def __init__(self, cell_x, cell_y, allo_x, allo_y, echo_interaction,hexa_memory):
        self.hexa_memory = hexa_memory
        self.cells = [(cell_x, cell_y)]
        self.allo_coordinates = [(allo_x, allo_y)]
        self.echo_interactions = [echo_interaction]
        self.center=(allo_x, allo_y)