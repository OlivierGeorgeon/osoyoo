class HexaCell:
    """This class represent a cell in a hexagrid
    """
    def __init__(self,x,y):
        """Constructor of the class, x and y are the coordinates of the cell
        """
        self.x = x
        self.y = y
        self.status = "Unknown"  # Status : "Free" (when has been visited), "Occupied" (when robot is on it), "Blocked" (when object is on it), "Unknown" (when has not been visited)
                              # "MovableObstacle" "Frontier"(when line) "Something"(when something echolocated) 
        self.occupied = False # True if the cell is occupied by the agent
        self.interactions = list() # Used in Synthesizer to store the interactions that happened on the cell
        self.confidence = 1

    def __str__(self):
        return "(" + str(self.x)+','+str(self.y) + ")"

    def occupy(self):
        self.occupied = True

    def leave(self):
        self.occupied = False

    def add_interaction(self,interaction):
        """Add a new interaction to the list of interactions
        """
        self.interactions.append(interaction)
        if not interaction in self.interactions:
            self.interactions.append(interaction)

            
    def set_to(self,status):
        """Change the cell status, print an error if the status is invalid.
        """
        if( status == "Free" or status == "Blocked" or status == "Unknown" or status == "Line" or status == "Something"): 
            self.status = status
        else :
            print("Unknown status : \" ",status, ", existing status : \"Free\" (when has been visited), \"Occupied\" (when robot is on it), \"Blocked\" (when object is on it), \"Unknown\" (when has not been visited)")