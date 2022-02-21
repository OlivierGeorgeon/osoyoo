class HexaCell:

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.status = "Unknown"  # Status : "Free" (when has been visited), "Occupied" (when robot is on it), "Blocked" (when object is on it), "Unknown" (when has not been visited)
                              # "MovableObstacle"

    def __str__(self):
        return "(" + str(self.x)+','+str(self.y) + ")"


    def set_to(self,status):
        if(status == "Occupied" or status == "Free" or status == "Blocked" or status == "Unknown"): 
            self.status = status
        else :
            print("Unknown status, existing status : \"Free\" (when has been visited), \"Occupied\" (when robot is on it), \"Blocked\" (when object is on it), \"Unknown\" (when has not been visited)")