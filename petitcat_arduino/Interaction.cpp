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
#include "led.h"
#include "Action_define.h"
#include "Robot_define.h"

Interaction::Interaction(Floor& FLO, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action) :
  _FLO(FLO), _HEA(HEA), _IMU(IMU), _WifiCat(WifiCat)
{
  // The received string must contain the action
  _action = ((const char*) json_action["action"])[0];
  if (_action == ACTION_TURN_IN_SPOT_LEFT)
    _target_angle = TURN_SPOT_ANGLE;  // Default left rotation
  if (_action == ACTION_TURN_IN_SPOT_RIGHT)
    _target_angle = -TURN_SPOT_ANGLE;  // Default right rotation

  // The received string must contain the clock
  _clock = (int)json_action["clock"];

  // The target angle used by Turn and by Turn_head if there is no focus
  if (json_action.hasOwnProperty("angle"))
    _target_angle = (int)json_action["angle"];

  // The focus point
  if (json_action.hasOwnProperty("focus_x"))
  {
    _focus_x = (int)json_action["focus_x"];
    _focus_y = (int)json_action["focus_y"];
    _focus_angle = atan2(_focus_y, _focus_x) * 180.0 / M_PI; // Direction of the focus relative to the robot
    _focus_distance = sqrt(sq((float)_focus_x) + sq((float)_focus_y));  // conversion to float is necessary for some reason
    _is_focussed = true;
  }
  else
    _is_focussed = false;

  // The speed used to keep focus and to specify swipe direction
  if (json_action.hasOwnProperty("speed"))
    _speed = (int)json_action["speed"];  // Is automatically converted to float
  else if (_action == ACTION_SHIFT_RIGHT)
    _speed = -_speed;  // Negative by default

  // The target duration used if there is no focus
  if (json_action.hasOwnProperty("duration"))
    _target_duration = (int)json_action["duration"];

  // If caution > 0 then check for obstacle when moving forward
  if (json_action.hasOwnProperty("caution"))
    _caution = (int)json_action["caution"];

  // The saccade span for scan interaction
  if (json_action.hasOwnProperty("span"))
    _span = (int)json_action["span"];

  // The instruction to align head after the enaction
  if (json_action.hasOwnProperty("align"))
    _align = (int)json_action["align"];

  _action_start_time = millis();
  _action_end_time = _action_start_time + _target_duration;
//  _status.reserve(10);
//  _status = "0"; // in interaction.h
//  _step = INTERACTION_BEGIN;  in interaction.h
}

void Interaction::begin()
{
  Serial.println("Method Interaction.step0() must be overridden!");
}

void Interaction::ongoing()
{
}

void Interaction::outcome(JSONVar & outcome_object)
{
}

// Wait for the interaction to terminate and proceed to Step 3
// Wait for Floor change retreat completed otherwise the wifi send interfers with the retreat
// Wait for Head alignment completed otherwise the head signal sent comes from before the interaction
// Warning: in some situations, the head alignment may take quite long

void Interaction::terminate()
{
  // Turn on the color sensor led
  _FLO._CLR.begin_read();

  // If is retreating then wait for immobilization
  if (_FLO._is_retreating)
    _action_end_time = millis() + 200;

  // When time is over then read the floor color and proceed to step SEND
  if (_action_end_time < millis() && (_align == 0 || !_HEA._is_enacting_head_alignment) && _FLO._CLR.end_read())
    _step = INTERACTION_SEND;

//  if (_action_end_time < millis() && !_HEA._is_enacting_head_alignment)
//  {
//    // Read the floor color and return true when done
//    if (_FLO._CLR.end_read())
//      // When color has been read, proceed to step 3
//      _step = INTERACTION_SEND;
//  }
}

// Send the outcome and go back to Step 0

void Interaction::send()
{
  // Serial.println("Interaction.step3()");
  // Compute the outcome message
  JSONVar outcome_object;
  outcome_object["clock"] = _clock;
  char s[2]; s[0] = _action; s[1] = 0;
//  snprintf(s, 2, "%c", _action);
  outcome_object["action"] = s;  // String(_action); Avoid String to improve memory management
  outcome_object["duration1"] = _duration1;
  _HEA.outcome(outcome_object);
  _FLO.outcome(outcome_object);
  _IMU.outcome(outcome_object);

  outcome_object["duration"] = millis() - _action_start_time;

  // The outcome for the specific interaction subclass
  outcome(outcome_object);
  outcome_object["status"] = _status;

  // Check if the robot touches an object with the contact sensor
  if (!digitalRead(TOUCH_PIN))
    outcome_object["touch"] = 1;

  // Send the outcome to the PC
  String outcome_json_string = JSON.stringify(outcome_object);
  // light the led during transfer
  #if LED_BUILTIN != ROBOT_SERVO_PIN
    digitalWrite(LED_BUILTIN, HIGH);
  #endif
  _WifiCat.send(outcome_json_string);
  #if LED_BUILTIN != ROBOT_SERVO_PIN
    digitalWrite(LED_BUILTIN, LOW);
  #endif

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

int Interaction::direction()
{
 return DIRECTION_FRONT;
}