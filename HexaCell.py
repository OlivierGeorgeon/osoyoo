class HexaCell:
    """This
    """
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.status = "Unknown"  # Status : "Free" (when has been visited), "Occupied" (when robot is on it), "Blocked" (when object is on it), "Unknown" (when has not been visited)
                              # "MovableObstacle" "Frontier"(when line) "Something"(when something echolocated) 
        self.occupied = False
        self.interactions = list()

    def __str__(self):
        return "(" + str(self.x)+','+str(self.y) + ")"

    def occupy(self):
        self.occupied = True

    def leave(self):
        self.occupied = False
        
    def set_to(self,status):
        """Change the cell status, print an error if the status is invalid.
        """
        if( status == "Free" or status == "Blocked" or status == "Unknown" or status == "Line" or status == "Something"): 
            self.status = status
        else :
            print("Unknown status, existing status : \"Free\" (when has been visited), \"Occupied\" (when robot is on it), \"Blocked\" (when object is on it), \"Unknown\" (when has not been visited)")