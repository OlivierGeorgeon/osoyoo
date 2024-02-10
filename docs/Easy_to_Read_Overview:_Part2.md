

# An Easy-to-Read Overview of the Robot Car Project: Modifying for Python Control

##

Initial draft Feb 9, 2024

(This is a public document that can be modified by others who have access -- if anything doesn't make sense, please ignore. A year from now, for example, I may not be aware of the full contents of this document any longer or what is still current.)
(No use of high voltage or anything dangerous is specified in this document.)
(The use of a horseback ride below is only a metaphor -- horses are pretty big in real life and quite scary to get on and even more scary to fall off:)
(Questions, corrections, suggestions? -- please contact me via my GitHub link.)
##

Welcome!! Bienvenue!! Tunngasugit!!

(I am in Canada -- these are our official languages -- English, French and a semi-official third (indigenous) language of Inuktitut.)

You have already built your Osoyoo Robot Car and learned how to modify and upload its software (well.... change some parameters at least). 

In this second part to our adventure, we will now turn the toy-like robot car into a serious Python controlled autonomous robot.

Saddle up!! Let's get going on the most exciting part of our journey....

![horsetonextlesson](horsetonextlesson.png)


# under construction#
information below taken from Olivier's GitHub documentation, and will be incorporated into the documentation


# 1   install libraries into IDE #

This project uses the following libraries:

Library	Function	Where to find it
Servo		Installed by default with the Arduino IDE
HC-SR04	Ultrasonic telemeter	Regular Osoyoo robot
WifiEsp-master	Wifi Shield	Regular Osoyoo robot (Lesson 5 : WiFiEsp-master.zip)
Arduino_JSON	JSON	Arduino IDE Library manager
MPU6050	Inertial Measurement Unit	Included in our project repository
HLC5883L	Compass	jarzebski github
MMC5883	Compass	Included in our project repository


nformation about these libraries
MPU6050
I adapted the MPU6050 library by Korneliusz Jarzebski and included it in this project. I had to add a timeout to avoid freezing the main loop if the MPU6050 is not responding. This seems to happen because of the noise caused by the motors. In file MPU6050.cpp, I added this line after Wire.begin() in line 38 (documentation here):

Wire.setWireTimeout( 25000, true);
Also, I had to edit the MPU6050.cpp to prevent it from aborting the initialization process when the address is not 0x68:

Modif MU6050_library

Figure 2: Comment the return false; in line 56

After looking at a few alternatives, I chose this library because it was also provided with my Arduino kit by Elegoo. It is provided in the arduino-kits-support-files. The file Mega_2560_The_Most_Complete_Starter_Kit contains the whole pedagogical material, including the electronic wiring diagram.

Arduino_JSON
Install Arduino_JSON by Arduino from the library manager: Install_Arduino_json

Don't mistake it with the library ArduinoJSON by Benoit Blanchon.

HMC5883L
This library handles the compass chip HMC5883L implemented in some of the GY-86 imu cards, It is available at https://github.com/jarzebski/Arduino-HMC5883L.

HMC5883L Figure 3: The IMU card with the compass chip labeled L883/2131.

If your compass chip begins with L883, include the following lines in robot_define.h for your robot:

#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 1
MMC5883L
This library handles the compass chip Duinotech MMC5883L implemented in some imu cards. I followed the article by David Such that lists the different compass chips. I adapted this library from his repo.

IMU Figure 4: The IMU card with the compass chip labeled 5883/601X.

If your compass chip begins with 5883, include the following lines in robot_define.h for your robot:

#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 2
Local parameters
Wifi
In the autocat_enacter\src\wifi folder, next to the WifiCat.cpp and WifiCat.h files, create the file arduino_secrets.h

To let the robot connect to your own wifi as a station (STA), arduino_secrets.h must contain:

#define SECRET_WIFI_TYPE "STA"
#define SECRET_SSID "<your wifi SSID>"
#define SECRET_PASS "<your password>"
Alternatively, to let the robot provide its own wifi osoyoo_robot as an access point (AP), arduino_secrets.h must contain:

#define SECRET_WIFI_TYPE "AP"



# 2 load autocat_enacter.ino sketch and associated files #

/*
 ____    ___  ______  ____  ______    __   ____  ______
|    \  /  _]|      ||    ||      |  /  ] /    ||      |
|  o  )/  [_ |      | |  | |      | /  / |  o  ||      |
|   _/|    _]|_|  |_| |  | |_|  |_|/  /  |     ||_|  |_|
|  |  |   [_   |  |   |  |   |  | /   \_ |  _  |  |  |
|  |  |     |  |  |   |  |   |  | \     ||  |  |  |  |
|__|  |_____|  |__|  |____|  |__|  \____||__|__|  |__|

 Upload autocat_enacter.ino to the OSOYOO robot car

  2023
    Olivier Georgeon
  Spring 2022
   Titouan Knockart, Université Claude Bernard (UCBL), France
  BSN2 2021-2022
   Aleksei Apostolou, Daniel Duval, Célien Fiorelli, Geordi Gampio, Julina Matouassiloua
  Teachers
   Raphaël Cazorla, Florian Tholin, Olivier Georgeon
  Bachelor Sciences du Numérique. ESQESE. UCLy. France

 Inspired form Arduino Mecanum Omni Direction Wheel Robot Car http://osoyoo.com/?p=30022
*/

#include <Arduino_JSON.h>
#include "src/wifi/WifiCat.h"
#include "Action_define.h"
#include "Floor.h"
#include "Head.h"
#include "Imu.h"
#include "Interaction.h"
#include "Led.h"
#include "Robot_define.h"
#include "Sequencer.h"

Floor FLO;
Head HEA;
Imu IMU;
WifiCat WifiCat;
Led LED;
Sequencer SEQ(FLO, HEA, IMU, LED, WifiCat);

int interaction_step = 0;
int interaction_direction = 0;
Interaction* INT  = nullptr;  // The interaction type will depend on the action received from the PC

void setup()
{
  // Initialize serial for debugging

  Serial.begin(9600);
  Serial.println("Serial initialized");

  // Initialize the LEDs

  LED.setup();

  // First attempt to initialize IMU

  IMU.setup();
  Serial.println("-- IMU initialized");

  // Connect to the wifi board

  WifiCat.begin();

  // Second attempt to initialize IMU (try again because sometimes it fails the first time)
  // Perhaps something to do with the order in which the imu registers are written.

  IMU.setup();
  Serial.println("-- IMU initialized");

  // Initialize the automatic behaviors

  FLO.setup();
  Serial.println("-- Wheels initialized");

  HEA.setup();
  Serial.println("-- Head initialized");

  Serial.println("--- Robot is ready ---");

  pinMode(TOUCH_PIN, INPUT_PULLUP);
}

void loop()
{
  // Control the built-in led and the emotion led

  LED.update();

  // Behavior Floor Change Retreat

  FLO.update(interaction_direction);

  // Behavior Head Echo Alignment

  HEA.update();

  // Behavior IMU

  IMU.update(interaction_step);

  // Watch for message received from PC. If yes, starts the interaction

  if (interaction_step == INTERACTION_DONE)
    INT = SEQ.update(interaction_step, INT);

  // Update the current interaction and return INTERACTION_DONE when done

  if (INT != nullptr)
  {
    interaction_step = INT->update();
    interaction_direction = INT->direction();
  }
  else
    interaction_direction = DIRECTION_FRONT;
}


# 3 wifi #

In the autocat_enacter\src\wifi folder, next to the WifiCat.cpp and WifiCat.h files, create the file arduino_secrets.h

To let the robot connect to your own wifi as a station (STA), arduino_secrets.h must contain:

#define SECRET_WIFI_TYPE "STA"
#define SECRET_SSID "<your wifi SSID>"
#define SECRET_PASS "<your password>"
Alternatively, to let the robot provide its own wifi osoyoo_robot as an access point (AP), arduino_secrets.h must contain:

#define SECRET_WIFI_TYPE "AP"
The robot's IP address will show in the serial terminal:


# 4 PetitCat #

Test the PetitCat Robot
This page explains how to test the PetitCat robot using the PetitCatTester.py file. Alternatively, you can use the PetitCatTester.ipynb notebook.


![python](python.png)



#!/usr/bin/env python
# Olivier Georgeon, 2023.
# This code is used to teach Developmental AI.
# Requires:
#   - A PetiCat robot https://github.com/OlivierGeorgeon/osoyoo/wiki

import socket
import keyboard
import sys
import json

UDP_IP = "192.168.4.1"
UDP_TIMEOUT = 5  # Seconds


class PetitCatTester:
    def __init__(self, ip, time_out, port=8888):
        self.IP = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(time_out)
        self.clock = 0
        self.focus_x = None
        self.focus_y = None
        self.color = None
        self.duration = None
        self.angle = None
        self.span = None

    def enact(self, _action_string):
        """ Sending the action string, waiting for the outcome, and returning the outcome bytes """
        _outcome = None  # Default if timeout
        # print("sending " + action)
        self.socket.sendto(bytes(_action_string, 'utf-8'), (self.IP, self.port))
        try:
            _outcome, address = self.socket.recvfrom(512)
        except socket.error as error:  # Time out error when robot is not connected
            print(error)
        return _outcome

    def send(self, _action):
        """Format the action string for the notebook"""
        command_dict = {'clock': self.clock, 'action': _action}
        if self.focus_x is not None:
            command_dict['focus_x'] = self.focus_x
        if self.focus_y is not None:
            command_dict['focus_y'] = self.focus_y
        if self.color is not None:
            command_dict['color'] = self.color
        if self.duration is not None:
            command_dict['duration'] = self.duration
        if self.angle is not None:
            command_dict['angle'] = self.angle
        _action_string = json.dumps(command_dict)
        print("Sending packet:", _action_string)
        _outcome = self.enact(_action_string)
        print("Received packet:", _outcome)
        if _outcome is not None:
            self.clock += 1
        print("Next clock:", self.clock)
        return _outcome


# Test the wifi interface by controlling the robot from the console
# Provide the Robot's IP address as a launch argument
# py PetitCatTester.py 192.168.8.242
if __name__ == '__main__':
    robot_ip = UDP_IP
    if len(sys.argv) > 1:
        robot_ip = sys.argv[1]
    else:
        print("Please provide your robot's IP address")
    print("Connecting to robot: " + robot_ip)
    print("Action keys: 1: Turn left, 2: Backward, 3: Turn right, 4: Swipe left, 6: Swipe right, 8: Forward, -: Scan")
    print("Ctrl+C and ENTER to abort")
    osoyoo_wifi = PetitCatTester(robot_ip, UDP_TIMEOUT)
    clock = 0
    action = ""
    while True:
        print("Press action key:")
        action = keyboard.read_key().upper()
        action_string = '{"clock":' + str(clock) + ', "action":"' + action + '"}'
        print("Sending packet:", action_string)
        outcome = osoyoo_wifi.enact(action_string)
        print("Received packet:", outcome)
        if outcome is not None:
            clock += 1




Run the test
Switch on the robot and read its IP address in the Arduino IDE terminal.

Make sure your PC is connected to the same wifi as the robot.

Clone this project or download the file PetitCatTester.py.

Run PetitCatTester.py with the IP address of you robot as an argument. For example:

py PetitCatTester.py 192.168.8.242
Press the action keys. The robot executes your commands. Your python terminal displays the logs as in Figure 1.

PetitCatTester Figure 1: The trace showing the enaction of three interactions

When you press a key, the program sends the command packet to the robot via UDP. The field "clock" is an incremental number. The field "action" is your key. The robot executes your command and returns the outcome packet.

If the wifi connection fails, the timeout is triggered and the outcome packet is None. The clock is not incremented.

If the robot receives a command packet containing a clock equal to the clock previously received, it does not re-execute the command, and it immediately resends the latest outcome packet.

Table 1 summarizes the recognized actions. The choice of keys was made for a standard keyboard numerical pad. These actions are interrupted if the robot detects a black line on the floor or an impact against an obstacle.

Table 1: Main recognized commands

Action key	Command
1	Turn in the spot to the left by 45°
2	Move backward during 1000ms
3	Turn in the spot to the right by 45°
4	Swipe left during 1000ms
6	Swipe right during 1000ms
8	Move forward during 1000ms
-	Scan the environment with the head
Main command fields
Table 2 summarizes the main fields of the command packet sent to the robot. To try the optional fields, you must modify PetitCatTester.py. Some optional fields only apply to some commands indicated in the Command column.

Field	Command	Status	Description
"clock"	all	Required	The incremental number of the interaction since startup.
"action"	all	Required	The action code
"focus_x"	all except -	Optional	The x coordinates of the focus point in mm
"focus_y"	all except -	Optional	The y coordinates of the focus point in mm
"color"	all	Optional	The color code of the emotion led: 0: off, 1: white, 2: green, 3: bleue, 4: red, 5: orange.
"duration"	2, 4, 8	Optional	The duration of the translation in milliseconds
"angle"	1	Optional	The angle of rotation in degrees. Negative angles turn right
"span"	-	Optional	The span of the saccades during the scan in degrees
During the interaction, the robot will keep its head towards the focus point defined by "focus_x" and "focus_y" coordinates.


# 5 IMU Board (or possibly as an earlier step) mods  #

HMC5883L
This library handles the compass chip HMC5883L implemented in some of the GY-86 imu cards, It is available at https://github.com/jarzebski/Arduino-HMC5883L.

HMC5883L Figure 3: The IMU card with the compass chip labeled L883/2131.

If your compass chip begins with L883, include the following lines in robot_define.h for your robot:

#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 1
MMC5883L
This library handles the compass chip Duinotech MMC5883L implemented in some imu cards. I followed the article by David Such that lists the different compass chips. I adapted this library from his repo.

IMU Figure 4: The IMU card with the compass chip labeled 5883/601X.

If your compass chip begins with 5883, include the following lines in robot_define.h for your robot:

#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 2


# 6 install IMU and Color Sensor #
parts to install:

HMC5583L compass chip in GY-86 IMU (inertial measurement) card (??) or MC5883L chip (?? to check)

Connect the IMU card to the wifi Shield following Table 2 and Figure 1. Note that the calibration offset varies significantly depending on the position of the card on the robot.

Table 2: IMU Wiring

GY-86 Imu	MEGA2560 Wifi Shield
Vcc	3v3
GND	GND
SCL	SCL
SDA	SDA

able 2: PIN connection

TCS34725	MEGA2560	
3v3	3v	On the Wifi Shield, yellow slots
GND	GND	On the Wifi Shield, black
SDA	SDA 20	
SCL	SCL 21	
LED	53	Digital output
More information on the TCS34725 adafruit webpage.

Color sensor (TCS34725 ?? to check)  
Use the "long" two-hole version of the TCS34725. It has two LEDs, and the holes miraculously match holes on the robot platform (Figure 4). Wire it to the Arduino MEGA according to Table 2. Use PINs 20 and 21 for SDA and SCL because the other SDA and SCL PINs are used for the IMU. They are the same. For the power line, I used the 3v yellow PINs on the Wifi Shield. Alternatively, the VIN PIN can be connected to a 5V PIN (red).

Table 2: PIN connection

TCS34725	MEGA2560	
3v3	3v	On the Wifi Shield, yellow slots
GND	GND	On the Wifi Shield, black
SDA	SDA 20	
SCL	SCL 21	
LED	53	Digital output
More information on the TCS34725 adafruit webpage.


![lastparts](lastparts.png)


# 7 Emotion LED #

-did not buy yet the part but readily available locally


Figure 5: RGB LED with flat side on the left. The cathode is the longest lead.
![rgbled](rgbled.png)


Table 3: RGB LED connections

RGB LED		MEGA2560 / Wifi shield
Blue		2
Green		3
GND	10kΩ resistor	GND
Red		5






Figure 6: The common cathode RGB LED on pins 2, 3, 5, and its cathode connected to the ground via a 10kΩ resistor. Flat side on the right.
![emotionledinstall](emotionledinstall.jpeg)






