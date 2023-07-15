from . Workspace import Workspace
from .Robot.CtrlRobot import CtrlRobot
from .Display.EgocentricDisplay.CtrlEgocentricView import CtrlEgocentricView
from .Display.AllocentricDisplay.CtrlAllocentricView import CtrlAllocentricView
from .Display.BodyDisplay.CtrlBodyView import CtrlBodyView
from .Display.PhenomenonDisplay.CtrlPhenomenonView import CtrlPhenomenonView


class Flock:
    """The Flock handles communication between robots"""
    def __init__(self, arguments):
        """Create the flock of robots"""
        self.workspaces = {}
        self.ctrl_robots = {}
        self.ctrl_egocentric_views = {}
        self.ctrl_allocentric_views = {}
        self.ctrl_body_views = {}
        for i in range(2, len(arguments)):
            workspace = Workspace(arguments[1], arguments[i])
            self.workspaces[arguments[i]] = workspace
            self.ctrl_robots[arguments[i]] = CtrlRobot(workspace)
            self.ctrl_egocentric_views[arguments[i]] = CtrlEgocentricView(workspace)
            self.ctrl_egocentric_views[arguments[i]].view.set_caption("Robot " + arguments[i])
            self.ctrl_allocentric_views[arguments[i]] = CtrlAllocentricView(self.workspaces[arguments[i]])
            self.ctrl_allocentric_views[arguments[i]].view.set_caption("Robot " + arguments[i])
            self.ctrl_body_views[arguments[i]] = CtrlBodyView(self.workspaces[arguments[i]])
            self.ctrl_body_views[arguments[i]].view.set_caption("Robot " + arguments[i])

        # Create the views for the first robot
        self.ctrl_phenomenon_view = CtrlPhenomenonView(self.workspaces[arguments[2]])
        self.workspaces[arguments[2]].ctrl_phenomenon_view = self.ctrl_phenomenon_view

    def main(self, dt):
        """Update the robots"""
        for robot_id in self.workspaces.keys():
            self.ctrl_robots[robot_id].main(dt)  # Check if outcome received from the robot
            self.workspaces[robot_id].main(dt)
            self.ctrl_robots[robot_id].main(dt)  # Check if command to send to the robot
            self.ctrl_egocentric_views[robot_id].main(dt)
            self.ctrl_allocentric_views[robot_id].main(dt)
            self.ctrl_body_views[robot_id].main(dt)
        # self.ctrl_allocentric_view.main(dt)
        # self.ctrl_body_view.main(dt)
        self.ctrl_phenomenon_view.main(dt)

        # Pass the message from robot '2' to robot '1'
        if all(key in self.workspaces for key in ['1', '2']):
            self.workspaces['1'].receive_message(self.workspaces['2'].emit_message())
        # Pass the message from robot '3' to robot '1'
        if all(key in self.workspaces for key in ['3', '1']):
            self.workspaces['1'].receive_message(self.workspaces['3'].emit_message())
