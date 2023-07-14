#   ____  __ __  ______   ___     __   ____  ______
#  /    ||  |  ||      | /   \   /  ] /    ||      |
# |  o  ||  |  ||      ||     | /  / |  o  ||      |
# |     ||  |  ||_|  |_||  O  |/  /  |     ||_|  |_|
# |  _  ||  :  |  |  |  |     /   \_ |  _  |  |  |  
# |  |  ||     |  |  |  |     \     ||  |  |  |  |  
# |__|__| \__,_|  |__|   \___/ \____||__|__|  |__|  
#
# Run main.py with the robot's IP address:
# py -m main.py <Arena_ID> <Robot ID>
#
#  Spring 2022
#   Titoua Knockart, Université Claude Bernard (UCBL), France
#  BSN2 2021-2022
#   Aleksei Apostolou, Daniel Duval, Célien Fiorelli, Geordi Gampio, Julina Matouassiloua
#  Teachers
#   Raphaël Cazorla, Florian Tholin, Olivier Georgeon
#  Bachelor Sciences du Numérique. ESQESE. UCLy. France

import sys
import pyglet
from autocat import Flock, Workspace, CtrlRobot, CtrlEgocentricView, CtrlAllocentricView, CtrlBodyView, CtrlPhenomenonView
from playsound import playsound

if len(sys.argv) < 3:  # Argument 0 is "main.py" when launched in -m mode
    print("Please provide the arena ID and the robot ID as arguments")
    exit()

flock = Flock(sys.argv)

playsound('autocat/Assets/R5.wav', False)
pyglet.clock.schedule_interval(flock.main, 0.1)
pyglet.app.run()
