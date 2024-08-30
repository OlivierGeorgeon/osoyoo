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
import logging
import structlog
import csv
from petitbrain import Flock, TRACE_HEADERS, TRACE_FILE

# Try to fix some mouse-press issue on Mac but it does not solve the problem
# https://github.com/pyglet/pyglet/issues/171
pyglet.options['osx_alt_loop'] = True

# Configure the logger

# File handler formatter
file_formatter = logging.Formatter('%(message)s')
# Console handler formatter
# console_formatter = logging.Formatter('%(levelname)s: %(message)s')
console_formatter = logging.Formatter('%(message)s')
# File handler
file_handler = logging.FileHandler(TRACE_FILE)
file_handler.setLevel(logging.INFO)  # Set the log level for the file
file_handler.setFormatter(file_formatter)
# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Set the log level for the console
console_handler.setFormatter(console_formatter)
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])


# Define a custom processor to format the log into a CSV row
def csv_processor(logger, method_name, event_dict):
    # Extract values based on the headers defined
    values = [event_dict.get(key, '').__str__() for key in TRACE_HEADERS]
    # return values
    return ','.join(values)


# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="%H:%M:%S", utc=False),
        csv_processor
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
# Reset the trace file
with open(TRACE_FILE, mode='w', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(TRACE_HEADERS)


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
