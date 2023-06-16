/*
  Interaction.cpp - library for controlling an interaction
  Created by Olivier Georgeon, mai 26 2023
  released into the public domain
*/
#include <Arduino_JSON.h>
#include "src/wifi/WifiCat.h"
#include "Color.h"
#include "Floor.h"
#include "Head.h"
#include "Imu.h"
#include "Interaction.h"
#include "Action_define.h"

Interaction::Interaction(
  Floor& FCR,
  Head& HEA,
  Imu& IMU,
  WifiCat& WifiCat,
  JSONVar json_action) :
  // unsigned long action_end_time, char action, int clock, bool is_focussed, int focus_x, int focus_y, int focus_speed ) :
  _FCR(FCR), _HEA(HEA), _IMU(IMU), _WifiCat(WifiCat)
{
  // The received string must contain the action
  _action = ((const char*) json_action["action"])[0];

  // The received string must contain the clock
  _clock = (int)json_action["clock"];

  // The target angle used if there is no focus
  if (json_action.hasOwnProperty("angle"))
    _target_angle = (int)json_action["angle"];

  // The focus point
  if (json_action.hasOwnProperty("focus_x"))
  {
    _focus_x = (int)json_action["focus_x"];
    _focus_y = (int)json_action["focus_y"];
    _target_focus_angle = atan2(_focus_y, _focus_x) * 180.0 / M_PI; // Direction of the focus relative to the robot
    _is_focussed = true;
  }
  else
    _is_focussed = false;

  if (json_action.hasOwnProperty("speed"))
    _focus_speed = (int)json_action["speed"]; // Must be positive otherwise multiplication with unsigned long fails

  // The target duration used if there is no focus
  if (json_action.hasOwnProperty("duration"))
    _target_duration = (int)json_action["duration"];

  _action_start_time = millis();
  // _action_end_time = action_end_time;
  _action_end_time = _action_start_time + _target_duration;
  // _action = action;
  // _clock = clock;
  // _is_focussed = is_focussed;
  // _focus_x = focus_x;
  // _focus_y = focus_y;
  // _focus_speed = focus_speed;

  _status = "0";
  _step = INTERACTION_BEGIN;
}

void Interaction::begin()
{
  Serial.println("Method Interaction.step0() must be overridden!");
}

void Interaction::ongoing()
{
}

// Wait for the interaction to terminate and proceed to Step 3
// Wait for Floor change retreat completed otherwise the wifi send interfers with the retreat
// Wait for Head alignment completed otherwise the head signal sent comes from before the interaction
// Warning: in some situations, the head alignment may take quite long

void Interaction::terminate()
{
  // Serial.println("Interaction.step2()");
  if (_action_end_time < millis() &&  !_FCR._is_enacting && !_HEA._is_enacting_head_alignment)
  {
    // Read the floor color
    _FCR._CLR.read();
    // Proceed to step 3
    _step = INTERACTION_SEND;
  }
}

// Send the outcome and go back to Step 0

void Interaction::send()
{
  // Serial.println("Interaction.step3()");
  // Compute the outcome message
  JSONVar outcome_object;
  outcome_object["status"] = _status;
  outcome_object["action"] = String(_action);
  outcome_object["clock"] = _clock;
  // _CLR.outcome(outcome_object);
  _FCR.outcome(outcome_object);
  _HEA.outcome(outcome_object);
  _HEA.outcome_complete(outcome_object);
  _IMU.outcome(outcome_object, _action);

  // HECS.outcome(outcome_object);
  outcome_object["duration1"] = _duration1;
  outcome_object["duration"] = millis() - _action_start_time;

  // Send the outcome to the PC
  String outcome_json_string = JSON.stringify(outcome_object);
  digitalWrite(LED_BUILTIN, HIGH); // light the led during transfer
  _WifiCat.send(outcome_json_string);
  digitalWrite(LED_BUILTIN, LOW);

  // Ready to delete this interaction
  _step = INTERACTION_DONE;
}

// Proceed with the enaction of the interaction

int Interaction::update()
{
  // STEP 0: Begin the interaction
  if (_step == INTERACTION_BEGIN)
    begin();

  // STEP 1: Enacting the interaction
  if (_step == INTERACTION_ONGOING)
    ongoing();

  // STEP 2: Enacting the termination of the interaction: Floor change retreat, Stabilisation time
  if (_step == INTERACTION_TERMINATE)
    terminate();

  // STEP 3: Ending the interaction:
  if (_step == INTERACTION_SEND)
    send();

  return _step;
}
