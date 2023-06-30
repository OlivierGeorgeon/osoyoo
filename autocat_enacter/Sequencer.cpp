/*
  Sequencer.cpp - library to control the sequences of interaction.
  Created Olivier Georgeon June 16 2023
  Released into the public domain
  https://github.com/arduino-libraries/Arduino_JSON/blob/master/examples/JSONObject/JSONObject.ino
*/

#include "Sequencer.h"

#include "src/wifi/WifiCat.h"
#include "Robot_define.h"
#include "Action_define.h"
#include "Color.h"
#include "Floor.h"
#include "Head.h"
#include "Imu.h"
#include "Interaction.h"
#include "Action_define.h"
#include "src/interactions/Circumvent.h"
#include "src/interactions/Backward.h"
#include "src/interactions/Forward.h"
#include "src/interactions/Scan.h"
#include "src/interactions/Swipe_left.h"
#include "src/interactions/Swipe_right.h"
#include "src/interactions/Turn.h"
#include "src/interactions/Turn_head.h"
// #include "src/interactions/Turn_left.h"
// #include "src/interactions/Turn_right.h"
#include "src/interactions/Watch.h"

Sequencer::Sequencer(Floor& FLO, Head& HEA, Imu& IMU, WifiCat& WifiCat) :
  _FLO(FLO), _HEA(HEA), _IMU(IMU), _WifiCat(WifiCat)
{
}

// Watch the wifi and returns the new interaction to enact if any
Interaction* Sequencer::update(int& interaction_step, Interaction* INT)
{
  digitalWrite(LED_BUILTIN, HIGH); // light the led during transfer
  int len = _WifiCat.read(packetBuffer);
  digitalWrite(LED_BUILTIN, LOW);

  // If received a new action

  if (len > 0)
  {
    char action = 0;
    int clock = 0;

    JSONVar json_action = JSON.parse(packetBuffer);
    // Serial.println(myObject);
    if (json_action.hasOwnProperty("action"))
      action = ((const char*) json_action["action"])[0];

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
      _IMU.begin();
      _FLO._floor_outcome = 0; // Reset possible floor change when the robot was placed on the floor

      // Instantiate the interaction

      if (action == ACTION_TURN_IN_SPOT_LEFT)
        INT = new Turn(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_GO_BACK)
        INT = new Backward(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_TURN_IN_SPOT_RIGHT)
        INT = new Turn(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_SHIFT_LEFT)
        INT = new Swipe_left(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_STOP)
        _FLO._OWM.stopMotion();

      else if (action == ACTION_SHIFT_RIGHT)
        INT = new Swipe_right(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_GO_ADVANCE)
        INT = new Forward(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_TURN_RIGHT)
        INT = new Circumvent(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_SCAN_DIRECTION)
        INT = new Turn_head(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_ECHO_SCAN)
        INT = new Scan(_FLO, _HEA, _IMU, _WifiCat, json_action);

//      else if (action == ACTION_ALIGN_ROBOT)
//        INT = new Turn_angle(_FLO, _HEA, _IMU, _WifiCat, json_action);
//
      else if (action == ACTION_WATCH)
        INT = new Watch(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else
      {
        // Unrecognized action (for debug)
        interaction_step = INTERACTION_DONE;  // remain in step 0
        _WifiCat.send("{\"status\":\"Unknown\", \"action\":\"" + String(action) + "\"}");
      }
    }
  }
  return INT;
}
