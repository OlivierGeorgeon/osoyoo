/*   >> Howard debug version trace <<
 ____    ___  ______  ____  ______    __   ____  ______
|    \  /  _]|      ||    ||      |  /  ] /    ||      |
|  o  )/  [_ |      | |  | |      | /  / |  o  ||      |
|   _/|    _]|_|  |_| |  | |_|  |_|/  /  |     ||_|  |_|
|  |  |   [_   |  |   |  |   |  | /   \_ |  _  |  |  |
|  |  |     |  |  |   |  |   |  | \     ||  |  |  |  |
|__|  |_____|  |__|  |____|  |__|  \____||__|__|  |__|

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
//#include "Interaction.h"
#include "Led.h"
#include "Robot_define.h"
#include "Sequencer.h"

Floor FLO;
Head HEA;
Imu IMU;
WifiCat WIF;
Led LED;
Sequencer SEQ(FLO, HEA, IMU, LED, WIF);

int interaction_step = INTERACTION_DONE;
int interaction_direction = DIRECTION_FRONT;
//Interaction* INT  = nullptr;  // The interaction type will depend on the action received from the PC

void setup()
{
  // Initialize

  Serial.begin(9600);
  Serial.print("Petitcat Arduino 0.1.3 for Robot ");
  Serial.println(ROBOT_ID);

  // Initialize the LEDs

  LED.setup();

  // First attempt to initialize IMU

  IMU.setup();

  // Connect to the wifi board

  WIF.begin();

  // Second attempt to initialize IMU (try again because sometimes it fails the first time)
  // Perhaps needs time after switch on
  // Perhaps something to do with the order in which the imu registers are written.

  IMU.setup();

  // Initialize the automatic behaviors

  FLO.setup();
  Serial.println("-- Wheels initialized");

  HEA.setup();
  Serial.println("-- Head initialized");

  pinMode(TOUCH_PIN, INPUT_PULLUP);

  Serial.println("--- Robot is ready ---");
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

  // Watch out for message received from PC. If message received, get the interaction

  //if (interaction_step == INTERACTION_DONE)
//  INT = SEQ.update(interaction_step, interaction_direction, INT);
  SEQ.update(interaction_step, interaction_direction);

  // Update the current interaction and return INTERACTION_DONE when done

//  if (INT != nullptr)
//  {
//    interaction_step = INT->update();
    // interaction_direction = INT->direction();
//  }
  // else
    // interaction_direction = DIRECTION_FRONT;
}
