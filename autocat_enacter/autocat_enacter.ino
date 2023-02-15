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
// #include "arduino_secrets.h"
#include "Robot_define.h"
#include "Floor.h"
#include "Head.h"
#include "Imu.h"
#include "Action_define.h"
#include "src/wifi/WifiCat.h"
#include "Led.h"
#include "src/steps/Step0.h"

// "Wheel.h" is imported by Floor.h
// #include "Head_echo_complete_scan.h"

Wheel OWM;
Floor FCR(OWM);
Head HEA;
Imu IMU;
//Head_echo_complete_scan HECS;
char packetBuffer[100]; // Max number of characters received
WifiCat WifiCat;
Led LED;

void setup()
{
  // Initialize serial for debugging
  Serial.begin(9600);
  Serial.println("Serial initialized");

  // Connect to the wifi board
  WifiCat.begin();

  // Initialize the automatic behaviors
  OWM.setup();
  HEA.setup();
  IMU.setup();
  //HECS.setup();
  // Setup the imu twice otherwise the calibration is wrong. I don't know why.
  // Probably something to do with the order in which the imu registers are written.
  delay(100);
  IMU.setup();
  delay(100);
  IMU.setup();

  Serial.println("--- Robot initialized ---");

  // Initialize PIN 13 LED for debugging
  pinMode(LED_BUILTIN, OUTPUT);
  //digitalWrite(LED_BUILTIN, HIGH);
}

unsigned long action_start_time = 0;
unsigned long duration1 = 0;
unsigned long action_end_time = 0;
int interaction_step = 0;
char action =' ';
String status = "0"; // The outcome information used for sequential learning
int robot_destination_angle = 0;
int head_destination_angle = 0;
int target_angle = 0;
int target_duration = 1000;
bool is_focussed = false;
int focus_x = 0;
int focus_y = 0;
int focus_speed = 180;
int clock = 0;
int previous_clock = -1;
int shock_event = 0;

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
  //digitalWrite(LED_BUILTIN, LOW); // for debug
  shock_event = IMU.update(interaction_step);
  // if (blink_on) {digitalWrite(LED_BUILTIN, HIGH);} // for debug

  // STEP 0: no interaction being enacted
  // Watching for message sent from PC
  if (interaction_step == 0)
  {
    Step0();
  }

  // STEP 1: Performing the action until the termination conditions are triggered
  // When termination conditions are triggered, stop the action and proceed to step 2
  if (interaction_step == 1)
  {
    switch (action)
    {
      case ACTION_GO_ADVANCE:
        if (is_focussed){  // Keep the head towards the focus (HEA is inhibited during the action)
          HEA.turnHead(HEA.head_direction(focus_x - focus_speed * (millis()- action_start_time)/1000, focus_y));}
        if (shock_event > 0 && !FCR._is_enacting){
          // If shock then stop the go advance action
          duration1 = millis()- action_start_time;
          action_end_time = 0;
          OWM.stopMotion();
          interaction_step = 2;
          break;
        }
        // Check if Floor Change Retreat
        if (FCR._is_enacting) {
          FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
          status ="1";
          // Proceed to step 2 for enacting Floor Change Retreat
          duration1 = millis()- action_start_time;
          action_end_time = 0;
          interaction_step = 2;
        }
        // If no floor change, check whether duration has elapsed
        else if (action_end_time < millis()) {
          if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
          duration1 = millis()- action_start_time;
          OWM.stopMotion();
          interaction_step = 2;
        }
        break;
      case ACTION_GO_BACK:
        if (is_focussed)  // Keep the head towards the focus (HEA is inhibited during the action)
          {HEA.turnHead(HEA.head_direction(focus_x + focus_speed * (millis()- action_start_time)/1000, focus_y));}
        // Check if Floor Change Retreat
        if (FCR._is_enacting) {
          FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
          status ="1";
          // Proceed to step 2 for enacting Floor Change Retreat
          duration1 = millis()- action_start_time;
          action_end_time = 0;
          interaction_step = 2;
        }
        // If no floor change, check whether duration has elapsed
        else if (action_end_time < millis()) {
          if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
          duration1 = millis()- action_start_time;
          OWM.stopMotion();
          interaction_step = 2;
        }
        break;
      case ACTION_SHIFT_RIGHT:
        if (is_focussed){  // Keep the head towards the focus (HEA is inhibited during the action)
          HEA.turnHead(HEA.head_direction(focus_x, focus_y + focus_speed * (millis()- action_start_time)/1000));}
        // Check if Floor Change Retreat
        if (FCR._is_enacting) {
          FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
          status ="1";
          // Proceed to step 2 for enacting Floor Change Retreat
          duration1 = millis()- action_start_time;
          action_end_time = 0;
          interaction_step = 2;
        }
        // If no floor change, check whether duration has elapsed
        else if (action_end_time < millis()) {
          if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
          duration1 = millis()- action_start_time;
          OWM.stopMotion();
          interaction_step = 2;
        }
        break;
      case ACTION_SHIFT_LEFT:
        if (is_focussed){  // Keep the head towards the focus (HEA is inhibited during the action)
          HEA.turnHead(HEA.head_direction(focus_x, focus_y - focus_speed * (millis()- action_start_time)/1000));}
        // Check if Floor Change Retreat
        if (FCR._is_enacting) {
          FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
          status ="1";
          // Proceed to step 2 for enacting Floor Change Retreat
          duration1 = millis()- action_start_time;
          action_end_time = 0;
          interaction_step = 2;
        }
        // If no floor change, check whether duration has elapsed
        else if (action_end_time < millis()) {
          if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
          duration1 = millis()- action_start_time;
          OWM.stopMotion();
          interaction_step = 2;
        }
        break;
      case ACTION_TURN_RIGHT:
      case ACTION_TURN_LEFT:
        // Check if Floor Change Retreat
        if (FCR._is_enacting) {
          FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
          status ="1";
          // Proceed to step 2 for enacting Floor Change Retreat
          duration1 = millis()- action_start_time;
          action_end_time = 0;
          interaction_step = 2;
        }
        // If no floor change, check whether duration has elapsed
        else if (action_end_time < millis()) {
          if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
          duration1 = millis()- action_start_time;
          OWM.stopMotion();
          interaction_step = 2;
        }
        break;
      case ACTION_TURN_IN_SPOT_LEFT:
        // Keep head aligned with destination angle
        if (is_focussed){
          //float current_robot_direction = (head_destination_angle - IMU._yaw) * M_PI / 180.0;
          float current_focus_direction = (target_angle - IMU._yaw) * M_PI / 180.0; // relative to robot
          float r = sqrt(sq((float)focus_x) + sq((float)focus_y));  // conversion to float is necessary for some reason
          float current_head_direction = HEA.head_direction(cos(current_focus_direction) * r, sin(current_focus_direction) * r);
          // Serial.println("Directions robot: " + String(current_robot_direction) + ", head: " + String((int)current_head_direction) + ", dist: " + String((int)r));
          HEA.turnHead(current_head_direction); // Keep looking at destination
        } else {
          HEA.turnHead(robot_destination_angle - IMU._yaw); // Keep looking at destination
        }
         // Stop before reaching destination angle or when duration has elapsed
        if ((IMU._yaw > robot_destination_angle - TURN_SPOT_ENDING_ANGLE) || (action_end_time < millis()))
        {
          if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
          duration1 = millis()- action_start_time;
          OWM.stopMotion();
          interaction_step = 2;
          action_end_time = millis() + TURN_SPOT_ENDING_DELAY; // Add time for stabilisation during step 2
        }
        break;
      case ACTION_TURN_IN_SPOT_RIGHT:
        // Keep head aligned with destination angle
        if (is_focussed){
          // float current_robot_direction = (head_destination_angle - IMU._yaw) * M_PI / 180.0;
          float current_focus_direction = (target_angle - IMU._yaw) * M_PI / 180.0;
          float r = sqrt(sq((float)focus_x) + sq((float)focus_y));  // conversion to float is necessary for some reason
          float current_head_direction = HEA.head_direction(cos(current_focus_direction) * r, sin(current_focus_direction) * r);
          // Serial.println("Directions robot: " + String(current_robot_direction) + ", head: " + String((int)current_head_direction) + ", dist: " + String((int)r));
          HEA.turnHead(current_head_direction); // Keep looking at destination
        } else {
          HEA.turnHead(robot_destination_angle - IMU._yaw); // Keep looking at destination
        }
        // Stop before reaching destination angle or when duration has elapsed
        if ((IMU._yaw < robot_destination_angle + TURN_SPOT_ENDING_ANGLE) || (action_end_time < millis()))
        {
          if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
          duration1 = millis()- action_start_time;
          OWM.stopMotion();
          interaction_step = 2;
          action_end_time = millis() + TURN_SPOT_ENDING_DELAY; // Add time for stabilisation during step 2
        }
        break;
      case ACTION_ALIGN_ROBOT:
        if (is_focussed){
          float current_robot_direction = (robot_destination_angle - IMU._yaw) * M_PI / 180.0;
          float r = sqrt(sq((float)focus_x) + sq((float)focus_y));  // conversion to float is necessary for some reason
          float current_head_direction = HEA.head_direction(cos(current_robot_direction) * r, sin(current_robot_direction) * r);
          // Serial.println("Directions robot: " + String(current_robot_direction) + ", head: " + String((int)current_head_direction) + ", dist: " + String((int)r));
          HEA.turnHead(current_head_direction); // Keep looking at destination
        } else {
          HEA.turnHead(robot_destination_angle - IMU._yaw); // Keep looking at destination
        }
        if (((robot_destination_angle > TURN_FRONT_ENDING_ANGLE) && (IMU._yaw > robot_destination_angle - TURN_FRONT_ENDING_ANGLE)) ||
        ((robot_destination_angle < -TURN_FRONT_ENDING_ANGLE) && (IMU._yaw < robot_destination_angle + TURN_FRONT_ENDING_ANGLE)) ||
        (abs(robot_destination_angle) < TURN_FRONT_ENDING_ANGLE))
        {
          if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
          duration1 = millis()- action_start_time;
          OWM.stopMotion();
          interaction_step = 2;
          action_end_time = millis() + TURN_FRONT_ENDING_DELAY;// give it time to immobilize before terminating interaction
        }
        break;
      case ACTION_ALIGN_HEAD:
      /*case ACTION_ECHO_COMPLETE:
        if(!HECS._is_enacting_echo_scan){
          action_end_time = 0;
          interaction_step = 2;
        }
        break;*/
      case ACTION_SCAN_DIRECTION:
        if (!HEA._is_enacting_head_alignment && !HEA._is_enacting_echo_scan)
        {
          duration1 = millis()- action_start_time;
          action_end_time = 0;
          interaction_step = 2;
        }
        break;
      case ACTION_ECHO_SCAN:
        if (!HEA._is_enacting_echo_scan)
        {
          if (!HEA._is_enacting_head_alignment) {HEA.beginEchoAlignment();}  // Force HEA
          duration1 = millis()- action_start_time;
          action_end_time = 0;
          interaction_step = 2;
        }
        break;
      default:
        if (action_end_time < millis()) {
          duration1 = millis()- action_start_time;
          OWM.stopMotion();
          interaction_step = 2;
        }
        break;
    }
  }

  // STEP 2: Enacting the termination of the interaction:
  // - Floor change retreat
  // - Stabilisation time
  // When the terminations are finished, proceed to Step 3
  if (interaction_step == 2)
  {
    // Wait for the interaction to terminate and proceed to Step 3
    // Warning: in some situations, the head alignment may take quite long
    if (action_end_time < millis() &&  !FCR._is_enacting && !HEA._is_enacting_head_alignment /*&& !HECS._is_enacting_echo_scan*/)
    {
      interaction_step = 3;
    }
  }

  // STEP 3: Ending of interaction:
  // Send the outcome and go back to Step 0
  if (interaction_step == 3)
  {
    // Compute the outcome message
    JSONVar outcome_object;
    outcome_object["status"] = status;
    outcome_object["action"] = String(action);
    outcome_object["clock"] = clock;
    FCR.outcome(outcome_object);
    HEA.outcome(outcome_object);
    HEA.outcome_complete(outcome_object);
    IMU.outcome(outcome_object, action);

    // HECS.outcome(outcome_object);
    outcome_object["duration1"] = duration1;
    outcome_object["duration"] = millis() - action_start_time;

    // Send the outcome to the PC
    String outcome_json_string = JSON.stringify(outcome_object);
    digitalWrite(LED_BUILTIN, HIGH); // light the led during transfer
    WifiCat.send(outcome_json_string);
    digitalWrite(LED_BUILTIN, LOW);

    // Ready to begin a new interaction
    interaction_step = 0;
  }
}
