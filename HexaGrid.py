from re import S
from HexaCell import HexaCell
class HexaGrid:
    """Inspired by http://roguebasin.com/?title=Hexagonal_Tiles#Coordinate_systems_with_a_hex_grid
    """

    def __init__(self,width,height):
        """Create a grid with hexagonal cells.
        Args : 
            width : number of cells in width
            height : number of cells in height

        """
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
        for j in range(self.height-1,-1,-1):
            if(j%2 == 1):
                    output += "-----"
            for i in range(self.width):
                
                output += str(self.grid[i][j])
                output += "-----"
            output += "\n"
        return output

    def getAllNeighbors(self,x,y):
        output = []
        for i in range(6):
            tmp = self.get_neighbor_in_direction(x,y,i)
            if not(tmp  == None):
                output.append(tmp)

        return output


    def get_neighbor_in_direction(self, x, y, direction):
        """Return the neighbor of the cell of coordinates x,y in the given direction 
        Args : Direction : 0 = N, 1 = NE, 2 = SE, 3 = S, 4 = SW, 5 = NW
        
        Return : HexaCell of the neighbor if it exists, otherwise None.
        """

        dTab = [(0,2),(0,1),(0,-1),(0,-2),(-1,-1),(-1,1),(0,-2)]
        dx,dy = dTab[direction]

        x += dx
        y += dy

        if( x < 0 or y < 0 or x >= self.width or y >= self.height):
            return None

        else :
            return self.grid[x][y]


if __name__ == '__main__':
    hx = HexaGrid(5,5)
    print(hx)
    print(hx.get_neighbor_in_direction(2,2,0))
    print("All neighbors of 2,2 : ", hx.getAllNeighbors(2,2))