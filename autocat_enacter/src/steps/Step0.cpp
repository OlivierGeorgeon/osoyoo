#include <Arduino_JSON.h>
#include "Step0.h"
#include "../wifi/WifiCat.h"
#include "../../Robot_define.h"
#include "../../Action_define.h"
#include "../../Floor.h"
#include "../../Head.h"
#include "../../Imu.h"

extern Wheel OWM;
extern Floor FCR;
extern Head HEA;
extern Imu IMU;
extern WifiCat WifiCat;
extern char packetBuffer[100];

extern unsigned long action_start_time;
extern unsigned long duration1;
extern unsigned long action_end_time;
extern int interaction_step;
extern char action;
extern String status; // The outcome information used for sequential learning
extern int robot_destination_angle;
extern int head_destination_angle;
extern int target_angle;
extern int target_duration;
extern int target_focus_angle;
extern bool is_focussed;
extern int focus_x;
extern int focus_y;
extern int focus_speed;
extern int clock;
extern int previous_clock;
extern int shock_event;


void Step0()
{
  // Watch the wifi for new action
  // If the received packet exceeds the size of packetBuffer defined above, Arduino will crash
  int len = WifiCat.read(packetBuffer);
  if (len) {
    //Serial.print("Received action ");
    target_angle = 0;
    target_duration = 1000;
    if (len == 1) {
      // Single character is the action
      action = packetBuffer[0];
      //Serial.print(action);
    } else {
      // Multiple characters is json
      // https://github.com/arduino-libraries/Arduino_JSON/blob/master/examples/JSONObject/JSONObject.ino
      JSONVar myObject = JSON.parse(packetBuffer);
      // Serial.println(myObject);
      if (myObject.hasOwnProperty("action")) {
        action = ((const char*) myObject["action"])[0];
      }
      if (myObject.hasOwnProperty("angle")) {
        target_angle = (int)myObject["angle"]; // for non-focussed
      }
      if (myObject.hasOwnProperty("focus_x")) {
        focus_x = (int)myObject["focus_x"];
        focus_y = (int)myObject["focus_y"];
        target_focus_angle = atan2(focus_y, focus_x) * 180.0 / M_PI; // Direction of the focus relative to the robot
        is_focussed = true;
      } else {
        is_focussed = false;
      }
      if (myObject.hasOwnProperty("speed")) {
        focus_speed = (int)myObject["speed"]; // Must be positive otherwise multiplication with unsigned long fails
      }
      if (myObject.hasOwnProperty("duration")) {
        target_duration = (int)myObject["duration"]; // for non-focussed
      }
      if (myObject.hasOwnProperty("clock")) {
        clock = (int)myObject["clock"];
      }
    }

    // If received the same action (same clock) then resend the outcome
    // (The previous outcome was sent but the PC did not receive it)
    if (clock == previous_clock) {
      interaction_step = 3;
    }
    else
    {
      previous_clock = clock;
      action_start_time = millis();
      action_end_time = action_start_time + 1000;
      interaction_step = 1;
      IMU.begin();
      shock_event = 0; // reset event from previous interaction
      FCR._floor_outcome = 0; // Reset possible floor change when the robot was placed on the floor
      //digitalWrite(LED_BUILTIN, LOW); // for debug
      status = "0";
      switch (action)
      {
        case ACTION_TURN_IN_SPOT_LEFT:
          HEA._next_saccade_time = action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
          action_end_time = millis() + TURN_SPOT_MAX_DURATION;
          robot_destination_angle = TURN_SPOT_ANGLE;
          if (is_focussed) {
            head_destination_angle = HEA.head_direction(focus_x, focus_y); // Look at the focus phenomenon
          } else {
            head_destination_angle = robot_destination_angle;}
          // HEA.turnHead(head_destination_angle); // Look at destination angle
          OWM.turnInSpotLeft(TURN_SPEED);
          break;
        case ACTION_GO_BACK:
          HEA._next_saccade_time = action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
          // if (is_focussed) {
          //  HEA.turnHead(HEA.head_direction(focus_x, focus_y));} // Turn head towards the focus point in step 1
          action_end_time = millis() + target_duration;
          OWM.goBack(SPEED);
          break;
        case ACTION_TURN_IN_SPOT_RIGHT:
          HEA._next_saccade_time = action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
          action_end_time = millis() + TURN_SPOT_MAX_DURATION;
          robot_destination_angle = -TURN_SPOT_ANGLE;
          if (is_focussed) {
            head_destination_angle = HEA.head_direction(focus_x, focus_y); // Look at the focus phenomenon
          } else {
            head_destination_angle = robot_destination_angle;}
          //HEA.turnHead(head_destination_angle); // Look at destination angle in step 1
          OWM.turnInSpotRight(TURN_SPEED);
          break;
        case ACTION_SHIFT_LEFT:
          HEA._next_saccade_time = action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
          OWM.shiftLeft(SHIFT_SPEED);
          //action_end_time = millis() + 5000;
          break;
        case ACTION_STOP:
          OWM.stopMotion();
          break;
        case ACTION_SHIFT_RIGHT:
          HEA._next_saccade_time = action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
          //action_end_time = millis() + 5000;
          OWM.shiftRight(SHIFT_SPEED);
          break;
        case ACTION_TURN_LEFT:
          action_end_time = millis() + 250;
          OWM.turnLeft(SPEED);
          break;
        case ACTION_GO_ADVANCE:
          HEA._next_saccade_time = action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
          action_end_time = millis() + target_duration;
          OWM.goForward(SPEED);
          break;
        case ACTION_TURN_RIGHT:
          action_end_time = millis() + 250;
          OWM.turnRight(SPEED);
          break;
        case ACTION_ALIGN_HEAD:
          HEA.beginEchoAlignment();
          action_end_time = millis() + 2000;
          break;
        case ACTION_SCAN_DIRECTION:
          if (is_focussed) {
            HEA.turnHead(HEA.head_direction(focus_x, focus_y));  // Look to the focussed phenomenon
          } else {
            HEA.turnHead(target_angle);}  // look parallel to the direction
          HEA.beginEchoAlignment();
          break;
        case ACTION_ECHO_SCAN:
          HEA.beginEchoScan();
          action_end_time = millis() + 2000;
          break;

        /*case ACTION_ECHO_COMPLETE:
          HECS.beginEchoScan();
          action_end_time = millis() + 5000;
          break;*/
        case ACTION_ALIGN_ROBOT:
          action_end_time = millis() + 5000;
          robot_destination_angle = target_angle;
          Serial.println("Begin align robot angle : " + String(robot_destination_angle));
          HEA._next_saccade_time = action_end_time - SACCADE_DURATION;  // Inhibit HEA during the interaction
          //if (is_focussed) {
          //  HEA.turnHead(HEA.head_direction(focus_x, focus_y));  // Look to the focussed phenomenon
          //} else {
          //  HEA.turnHead(robot_destination_angle);}  // look parallel to the direction
          if ( robot_destination_angle < - TURN_FRONT_ENDING_ANGLE){
            OWM.turnInSpotRight(TURN_SPEED);
            //OWM.turnFrontRight(SPEED);
          }
          if ( robot_destination_angle > TURN_FRONT_ENDING_ANGLE){
            OWM.turnInSpotLeft(TURN_SPEED);
            //OWM.turnFrontLeft(SPEED);
          }
          break;
        default:
          break;
      }
    }
  }
}