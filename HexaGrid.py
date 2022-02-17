from HexaCell import HexaCell
class HexaGrid:

    def __init__(self,width,height):
        self.grid = list()
        self.width = width
        self.height = height
        for i in range(width):
            self.grid.append(list())
            for j in range(height):
                self.grid[i].append(HexaCell(i,j))

    def __repr__(self): 
        return "Test a:% s b:% s" % (self.a, self.b) 
    
    def __str__(self): 
        output = ""
        for j in range(self.height):
            for i in range(self.width):
                output += str(self.grid[i][j])
            output += "\n"
        return output

    def getAllNeighbors(self):
        a = 0

    def get_neighbor_in_direction(self, x, y, direction):
        """Returns
        """



if __name__ == '__main__':
    hx = HexaGrid(5,5)
    print(hx)