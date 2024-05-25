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
#include "src/interactions/Swipe.h"
#include "src/interactions/Turn.h"
#include "src/interactions/Turn_head.h"
#include "src/interactions/Watch.h"
#include "src/interactions/Test.h"

// #include <MemoryUsage.h>

Sequencer::Sequencer(Floor& FLO, Head& HEA, Imu& IMU, Led& LED, WifiCat& WifiCat) :
  _FLO(FLO), _HEA(HEA), _IMU(IMU), _LED(LED), _WifiCat(WifiCat)
{
}

// Watch out the wifi and returns the new interaction to enact if any
Interaction* Sequencer::update(int& interaction_step, Interaction* INT)
{
  // Dim the led while waiting for a command
  _LED.builtin_on();
  int len = _WifiCat.read(_packetBuffer);
  _LED.builtin_off();

  // If received a new action

  if (len > 0)
  {
    char action = 0;
    int clock = 0;

    JSONVar json_action = JSON.parse(_packetBuffer);
    if (json_action.hasOwnProperty("action"))
      action = ((const char*) json_action["action"])[0];

    if (json_action.hasOwnProperty("clock"))
      clock = (int)json_action["clock"];

    // If the new clock equals the previous clock then do not enact the interaction but resend the previous outcome
    // (The interaction was already enacted but the PC did not receive the previous outcome)

    if (clock == _previous_clock)
    {
      if (INT != nullptr)
        INT->send();
    }

    // If the new clock differs from the previous clock then enact the interaction
    // (Lower clock means it was received from another PC application)

    else
    {
      // Delete the previous interaction (Not sure whether it is needed)
      if (INT != nullptr)
      {
        delete INT;
        INT = nullptr;
      }

      interaction_step = INTERACTION_BEGIN;
      _previous_clock = clock;
      _IMU.begin();
      _FLO._floor_outcome = 0; // Reset possible floor change when the robot was placed on the floor

      // Set the emotion led
      if (json_action.hasOwnProperty("color"))
        _LED.color((int)json_action["color"]);
      else
        _LED.color(0);

      // Instantiate the interaction

      if (action == ACTION_TURN_IN_SPOT_LEFT)
        INT = new Turn(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_GO_BACK)
        INT = new Backward(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_TURN_IN_SPOT_RIGHT)
        INT = new Turn(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_SHIFT_LEFT)
        INT = new Swipe(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_STOP)
      {
        // Do nothing. Can be used for debug
        interaction_step = INTERACTION_DONE;  // remain in step 0
        char s[40]; snprintf(s, 40, "{\"clock\":%d, \"action\":\"%c\"}", clock, action);
        _WifiCat.send(s);
      }

      else if (action == ACTION_SHIFT_RIGHT)  // Negative speed makes swipe to the right
        INT = new Swipe(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_GO_ADVANCE)
        INT = new Forward(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_TURN_RIGHT)
        INT = new Circumvent(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_SCAN_DIRECTION)
        INT = new Turn_head(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_ECHO_SCAN)
        INT = new Scan(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else if (action == ACTION_TEST)
        INT = new Test(_FLO, _HEA, _IMU, _WifiCat, json_action);

//      else if (action == ACTION_ALIGN_ROBOT)
//        INT = new Turn_angle(_FLO, _HEA, _IMU, _WifiCat, json_action);
//
      else if (action == ACTION_WATCH)
        INT = new Watch(_FLO, _HEA, _IMU, _WifiCat, json_action);

      else
      {
        // Unrecognized action (for debug)
        interaction_step = INTERACTION_DONE;  // remain in step 0
        char s[50];
        snprintf(s, 50, "{\"clock\":%d, \"action\":\"%c\", \"status\":\"Unknown\"}", clock, action);
//        snprintf(s, 40, "{\"status\":\"Unknown\", \"action\":\"%c\"}", action);
        _WifiCat.send(s);
      }

      // Print the address of the pointer to control that the heap is not going to overflow
      Serial.print("Interaction's address in SRAM: ");
      Serial.println((unsigned int)INT);
    }
  }
  return INT;
}
