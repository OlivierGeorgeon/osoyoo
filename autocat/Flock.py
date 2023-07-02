

class Flock:
    """The Flock handles communication between robots"""
    def __init__(self):
        self.robots = {}

    def get_robot_message(self, robot_id):
        """Get an answer message from a robot"""
        return self.robots[robot_id].answer_message()
