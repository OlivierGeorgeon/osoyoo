/*   >> Howard debug version trace <<
 ____    ___  ______  ____  ______    __  /\_/\  ______
|    \  /  _]|      ||    ||      |  /  ]/  o o||      |
|  o  )/  [_ |      | |  | |      | /  / |  >;<||      |
|   _/|    _]|_|  |_| |  | |_|  |_|/  /  |     ||_|  |_|
|  |  |   [_   |  |   |  |   |  | /   \_ |  _  |  |  |
|  |  |     |  |  |   |  |   |  | \     ||  |  |  |  |
|__|  |_____|  |__|  |____|  |__|  \____||_m|_m|  |__|

 Upload this file to the PetitCat robot car

  2024
    Karim Assi (UCly, ESQESE, BSN)
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

#include "src/wifi/WifiCat.h"
#include "Action_define.h"
#include "Floor.h"
#include "Head.h"
#include "Imu.h"
#include "Led.h"
#include "Robot_define.h"
#include "Sequencer.h"

Floor FLO;
Head HEA;
Imu IMU;
Led LED;
Sequencer ACT(FLO, HEA, IMU, LED);

int interaction_step = INTERACTION_DONE;
int interaction_direction = DIRECTION_FRONT;

void setup()
{
  // Initialize the serial com

  Serial.begin(9600);
  Serial.print("Petitcat Arduino 0.1.3 for Robot ");
  Serial.println(ROBOT_ID);

  // Initialize the LEDs

  LED.setup();

  // First attempt to initialize IMU

  IMU.setup();

  // Connect to the wifi

  ACT.setup();

  // Second attempt to initialize IMU (try again because sometimes it fails the first time)
  // Not sure why. Perhaps needs time after switched on
  // Perhaps something to do with the order in which the imu registers are written.

  IMU.setup();

  // Initialize the automatic behaviors

  FLO.setup();
  Serial.println("-- Floor monitoring initialized");

  HEA.setup();
  Serial.println("-- Head monitoring initialized");

  pinMode(TOUCH_PIN, INPUT_PULLUP);

  Serial.println("--- Petitcat is ready ---");
}

void loop()
{
  // Control the built-in LED and the emotion LED

  LED.update();

  // Behavior Floor Change Retreat

  FLO.update(interaction_direction);

  // Behavior Head Echo Alignment

  HEA.update();

  // Behavior IMU

  IMU.update(interaction_step);

  // Monitor the wifi and enact the interaction received from the PC
  //  (Update interaction_step and interaction_direction)

  ACT.update(interaction_step, interaction_direction);
}
