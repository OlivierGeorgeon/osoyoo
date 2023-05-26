/*
   ____  __ __  ______   ___     __   ____  ______
  /    ||  |  ||      | /   \   /  ] /    ||      |
 |  o  ||  |  ||      ||     | /  / |  o  ||      |
 |     ||  |  ||_|  |_||  O  |/  /  |     ||_|  |_|
 |  _  ||  :  |  |  |  |     /   \_ |  _  |  |  |
 |  |  ||     |  |  |  |     \     ||  |  |  |  |
 |__|__| \__,_|  |__|   \___/ \____||__|__|  |__|

 Download autocat_enacter.ino to the OSOYOO robot car

  Spring 2023
    Olivier Georgeon
  Spring 2022
   Titouan Knockart, Université Claude Bernard (UCBL), France
  BSN2 2021-2022
   Aleksei Apostolou, Daniel Duval, Célien Fiorelli, Geordi Gampio, Julina Matouassiloua
  Teachers
   Raphaël Cazorla, Florian Tholin, Olivier Georgeon
  Bachelor Sciences du Numérique. ESQESE. UCLy. France

 Inspired form Arduino Mecanum Omni Direction Wheel Robot Car Lesson5 Wifi Control
 Tutorial URL http://osoyoo.com/?p=30022
*/

#include <Arduino_JSON.h>
#include "Robot_define.h"
#include "Floor.h"  // imports "Wheel.h"
#include "Head.h"
#include "Imu.h"
#include "Color.h"
#include "Action_define.h"
#include "Led.h"
#include "Interaction.h"
#include "src/wifi/WifiCat.h"
#include "src/steps/Step0.h"
#include "src/steps/Step1.h"
#include "src/steps/Step2.h"
#include "src/steps/Step3.h"

Wheel OWM;
Floor FCR(OWM);
Head HEA;
Imu IMU;
WifiCat WifiCat;
Led LED;
Color TCS;
Interaction INT(TCS, FCR, HEA);
//Interaction INT(TCS, HEA);

unsigned long action_start_time = 0;
unsigned long duration1 = 0;
unsigned long action_end_time = 0;
char action =' ';
int interaction_step = 0;
int robot_destination_angle = 0;
int head_destination_angle = 0;
int target_angle = 0;
int target_duration = 1000;
int target_focus_angle = 0;
int focus_x = 0;
int focus_y = 0;
int focus_speed = 180;
int clock = 0;
int previous_clock = -1;
int shock_event = 0;
bool is_focussed = false;
String status = "0"; // The outcome information used for sequential learning

void setup()
{
  // Initialize serial for debugging
  Serial.begin(9600);
  Serial.println("Serial initialized");

  // Connect to the wifi board
  WifiCat.begin();

  // Initialize the automatic behaviors
  OWM.setup();
  Serial.println("Wheels initialized");
  HEA.setup();
  Serial.println("Head initialized");
  IMU.setup();
  // Setup the imu twice otherwise the calibration is wrong. I don't know why.
  // Probably something to do with the order in which the imu registers are written.
  delay(100);
  IMU.setup();
  delay(100);
  IMU.setup();
  Serial.println("IMU initialized");
  TCS.setup();
  Serial.println("Color sensor initialized");
  Serial.println("--- Robot initialized ---");

  // Initialize PIN 13 LED for debugging
  pinMode(LED_BUILTIN, OUTPUT);
  //digitalWrite(LED_BUILTIN, HIGH);
}

void loop()
{
  // Make the built-in led blink to show that the main loop is running properly
  LED.blink();

  // Behavior floor change retreat
  FCR.update();

  // Behavior head echo alignment
  HEA.update();

  // Behavior head echo complete scan
  //HECS.update();

  // Behavior IMU
  shock_event = IMU.update(interaction_step);

  // STEP 0: no interaction being enacted
  // Watching for message received from PC. If yes, starts the interaction
  if (interaction_step == 0)
    Step0();

  // STEP 1: Performing the action until the termination conditions are triggered
  // When termination conditions are triggered, stop the action and proceed to step 2
  if (interaction_step == 1)
    Step1();

  // STEP 2: Enacting the termination of the interaction: Floor change retreat, Stabilisation time
  // When the terminations are finished, proceed to Step 3
  if (interaction_step == 2)
    INT.Step2(action_end_time, interaction_step);
    //Step2();

  // STEP 3: Ending the interaction:
  // Send the outcome and go back to Step 0
  if (interaction_step == 3)
    Step3();
}
