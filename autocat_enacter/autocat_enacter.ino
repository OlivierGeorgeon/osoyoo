/*
   ____  __ __  ______   ___     __   ____  ______
  /    ||  |  ||      | /   \   /  ] /    ||      |
 |  o  ||  |  ||      ||     | /  / |  o  ||      |
 |     ||  |  ||_|  |_||  O  |/  /  |     ||_|  |_|
 |  _  ||  :  |  |  |  |     /   \_ |  _  |  |  |
 |  |  ||     |  |  |  |     \     ||  |  |  |  |
 |__|__| \__,_|  |__|   \___/ \____||__|__|  |__|

 Upload autocat_enacter.ino to the OSOYOO robot car

  Spring 2023
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
Sequencer SEQ(FLO, HEA, IMU, WifiCat);

int interaction_step = 0;
Interaction* INT  = nullptr;  // The interaction type will depend on the action received from the PC

void setup()
{
  // Initialize serial for debugging

  Serial.begin(9600);
  Serial.println("Serial initialized");

  // Initialize LEDs

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(BLUE_LED_PIN, OUTPUT);

  // First attempt to initialize IMU

  IMU.setup();

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
}

void loop()
{
  // Make the built-in led blink to show that the main loop is running properly

  LED.blink();

  // Behavior Floor Change Retreat

  FLO.update();

  // Behavior Head Echo Alignment

  HEA.update();

  // Behavior IMU

  IMU.update(interaction_step);

  // Watch for message received from PC. If yes, starts the interaction

  if (interaction_step == INTERACTION_DONE)
    INT = SEQ.update(interaction_step, INT);

  // Update the current interaction and return INTERACTION_DONE when done

  if (INT != nullptr)
    interaction_step = INT->update();
}
