#  ____    ___  ______  ____  ______    __  /\_/\  ______
# |    \  /  _]|      ||    ||      |  /  ]/  o o||      |
# |  o  )/  [_ |      | |  | |      | /  / |  >;<||      |
# |   _/|    _]|_|  |_| |  | |_|  |_|/  /  |     ||_|  |_|
# |  |  |   [_   |  |   |  |   |  | /   \_ |  _  |  |  |
# |  |  |     |  |  |   |  |   |  | \     ||  |  |  |  |
# |__|  |_____|  |__|  |____|  |__|  \____||_m|_m|  |__|
#
# Run main.py with the arena and robot IDs:
# py -m main.py <Arena_ID> <Robot ID1> <Robot ID2> ...
#
#  Spring 2024
#   Karim Assi (UCLy, ESQESE, BSN)
#  Spring 2022
#   Titoua Knockart, Université Claude Bernard (UCBL), France
#  2021-2022
#   Aleksei Apostolou, Daniel Duval, Célien Fiorelli, Geordi Gampio, Julina Matouassiloua (UCLy, ESQESE, BSN)
#  Teachers
#   Raphaël Cazorla, Florian Tholin, Olivier Georgeon
#  Bachelor Sciences du Numérique. ESQESE. UCLy. France

import sys
import pyglet
from autocat import Flock

# Try to fix some mouse-press issue on Mac but it does not solve the problem
# https://github.com/pyglet/pyglet/issues/171
pyglet.options['osx_alt_loop'] = True

# Check for the presence of the launch arguments
if len(sys.argv) < 3:  # Argument 0 is "main.py" when launched in -m mode
    print("Please provide the arena ID and the robot ID as arguments")
    exit()

# Initialize the flock of robots
flock = Flock(sys.argv)

# Schedule the GUI update every 100ms
pyglet.clock.schedule_interval(flock.main, 0.1)

# Launch the GUI
pyglet.app.run()
