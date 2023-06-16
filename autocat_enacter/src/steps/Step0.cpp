#include <Arduino_JSON.h>
#include "Step0.h"
#include "../wifi/WifiCat.h"
#include "../../Robot_define.h"
#include "../../Action_define.h"
#include "../../Color.h"
#include "../../Floor.h"
#include "../../Head.h"
#include "../../Imu.h"
#include "../../Interaction.h"
#include "../../Action_define.h"
#include "../interactions/Backward.h"
#include "../interactions/Forward.h"
#include "../interactions/Scan.h"
#include "../interactions/Swipe_left.h"
#include "../interactions/Swipe_right.h"
#include "../interactions/Turn_angle.h"
#include "../interactions/Turn_head.h"
#include "../interactions/Turn_left.h"
#include "../interactions/Turn_right.h"

char packetBuffer[UDP_BUFFER_SIZE];

extern Color CLR;
extern Wheel OWM;
extern Floor FCR;
extern Head HEA;
extern Imu IMU;
extern WifiCat WifiCat;

extern int interaction_step;
extern int previous_clock;
extern Interaction* INT;

void Step0()
{
  // Watch the wifi for new action

  digitalWrite(LED_BUILTIN, HIGH); // light the led during transfer
  int len = WifiCat.read(packetBuffer);
  digitalWrite(LED_BUILTIN, LOW);

  // If received a new action

  if (len > 0)
  {
    char action = 0;
    int clock = 0;
//    int target_angle = 0;
//    int target_duration = 1000;
//    int target_focus_angle = 0;
//    bool is_focussed = false;
//    int focus_x = 0;
//    int focus_y = 0;
//    int focus_speed = 0;
//    int robot_destination_angle;
//    int head_destination_angle;

    // https://github.com/arduino-libraries/Arduino_JSON/blob/master/examples/JSONObject/JSONObject.ino
    JSONVar json_action = JSON.parse(packetBuffer);
    // Serial.println(myObject);
    if (json_action.hasOwnProperty("action"))
      action = ((const char*) json_action["action"])[0];

//    if (json_action.hasOwnProperty("angle"))
//      target_angle = (int)json_action["angle"]; // for non-focussed
//
//    if (json_action.hasOwnProperty("focus_x"))
//    {
//      focus_x = (int)json_action["focus_x"];
//      focus_y = (int)json_action["focus_y"];
//      target_focus_angle = atan2(focus_y, focus_x) * 180.0 / M_PI; // Direction of the focus relative to the robot
//      is_focussed = true;
//    }
//    else
//      is_focussed = false;
//
//    if (json_action.hasOwnProperty("speed"))
//      focus_speed = (int)json_action["speed"]; // Must be positive otherwise multiplication with unsigned long fails
//
//    if (json_action.hasOwnProperty("duration"))
//      target_duration = (int)json_action["duration"]; // for non-focussed
//
    if (json_action.hasOwnProperty("clock"))
      clock = (int)json_action["clock"];

    // If received a string with the same clock then resend the outcome
    // (The previous outcome was sent but the PC did not receive it)

    if (clock == previous_clock)
    {
      if (INT != nullptr)
        INT->send();
    }

    // If it is a new clock then process the action

    else
    {
      // Delete the previous interaction (Not sure if it is needed)
      if (INT != nullptr)
      {
        delete INT;
        INT = nullptr;
      }

      interaction_step = INTERACTION_BEGIN;
      previous_clock = clock;
      // unsigned long action_end_time = millis() + target_duration;
      IMU.begin();
      FCR._floor_outcome = 0; // Reset possible floor change when the robot was placed on the floor

      // Instantiate the interaction

      if (action == ACTION_TURN_IN_SPOT_LEFT)
        INT = new Turn_left(FCR, HEA, IMU, WifiCat, json_action);
        // action_end_time, action, clock, is_focussed, focus_x, focus_y,focus_speed, target_angle, target_focus_angle);

      else if (action == ACTION_GO_BACK)
        INT = new Backward(FCR, HEA, IMU, WifiCat, json_action);
        //action_end_time, action, clock, is_focussed, focus_x, focus_y, focus_speed);

      else if (action == ACTION_TURN_IN_SPOT_RIGHT)
        INT = new Turn_right(FCR, HEA, IMU, WifiCat, json_action);
        // action_end_time, action, clock, is_focussed, focus_x, focus_y, focus_speed, target_angle, target_focus_angle);

      else if (action == ACTION_SHIFT_LEFT)
        INT = new Swipe_left(FCR, HEA, IMU, WifiCat, json_action);
        // action_end_time, action, clock, is_focussed, focus_x, focus_y, focus_speed);

      else if (action == ACTION_STOP)
        OWM.stopMotion();

      else if (action == ACTION_SHIFT_RIGHT)
        INT = new Swipe_right(FCR, HEA, IMU, WifiCat, json_action);
        // action_end_time, action, clock, is_focussed, focus_x, focus_y, focus_speed);

      else if (action == ACTION_GO_ADVANCE)
        INT = new Forward(FCR, HEA, IMU, WifiCat, json_action);
        // action_end_time, action, clock, is_focussed, focus_x, focus_y, focus_speed);

      else if (action == ACTION_SCAN_DIRECTION)
        INT = new Turn_head(FCR, HEA, IMU, WifiCat, json_action);
        // action_end_time, action, clock, is_focussed, focus_x, focus_y, focus_speed, target_angle);

      else if (action == ACTION_ECHO_SCAN)
        INT = new Scan(FCR, HEA, IMU, WifiCat, json_action);
        // action_end_time, action, clock, is_focussed, focus_x, focus_y, focus_speed);

      else if (action == ACTION_ALIGN_ROBOT)
        INT = new Turn_angle(FCR, HEA, IMU, WifiCat, json_action);
        // action_end_time, action, clock, is_focussed, focus_x, focus_y, focus_speed, target_angle);

      else
      {
        // Unrecognized action (for debug)
        interaction_step = INTERACTION_DONE;  // remain in step 0
        WifiCat.send("{\"status\":\"Unknown\", \"action\":\"" + String(action) + "\"}");
      }
    }
  }
}