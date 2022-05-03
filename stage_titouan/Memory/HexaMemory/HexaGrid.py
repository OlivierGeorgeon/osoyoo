from . HexaCell import HexaCell


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

    def get_all_neighbors(self,x,y):
        output = []
        for i in range(6):
            tmp = self.get_neighbor_in_direction(x,y,i)
            if not(tmp  == None):
                output.append(tmp)

        return output

    def get_all_neighbors_with_direction(self,x,y):
        output = []
        for i in range(6):
            tmp = self.get_neighbor_in_direction(x,y,i)
            if not(tmp  == None):
                output.append([tmp,i])

        return output

    def get_neighbor_in_direction(self, x, y, direction):
        """Return the neighbor of the cell of coordinates x,y in the given direction 
        Args : Direction : 0 = N, 1 = NE, 2 = SE, 3 = S, 4 = SW, 5 = NW
        
        Return : HexaCell of the neighbor if it exists, otherwise None.
        """

        if(direction < 0 or direction > 5):
            print("HexaGrid get neighbor_in_direction, invalid direction : ",direction)
        dTab_y_pair = [(0,2),(0,1),(0,-1),(0,-2),(-1,-1),(-1,1)]
        dTab_y_impair = [(0,2),(1,1),(1,-1),(0,-2),(0,-1),(0,+1)]

        if(y %2 == 0):
            dTab = dTab_y_pair
        else :
            dTab = dTab_y_impair
        dx,dy = dTab[direction]

        x += dx
        y += dy

        if( x < 0 or y < 0 or x >= self.width or y >= self.height):
            return None

        else :
            return self.grid[x][y]

    def add_interaction(self,x,y,interaction):
        """Add an interaction to the cell of coordinates x,y
        Args :
            x : x coordinate of the cell
            y : y coordinate of the cell
            interaction : interaction to add
        """
        self.grid[x][y].add_interaction(interaction)

if __name__ == '__main__':
    hx = HexaGrid(5,5)
    print(hx)
    print(hx.get_neighbor_in_direction(2,2,0))
    print("All neighbors of 2,2 : ", hx.get_all_neighbors(2,2))