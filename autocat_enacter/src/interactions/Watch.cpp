/*
  Watch.cpp - library for controlling the Watch interaction
  Watch for change in the echo distance. If change then align head and terminate the interaction
  If not change then trigger echo scan.
  Created by Olivier Georgeon, June 29 2023
  released into the public domain
*/
#include "../wifi/WifiCat.h"
#include "../../Action_define.h"
#include "../../Robot_define.h"
#include "../../Color.h"
#include "../../Floor.h"
#include "../../Head.h"
#include "../../Imu.h"
#include "../../Interaction.h"
#include "Watch.h"

Watch::Watch(Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action) :
  Interaction(FCR, HEA, IMU, WifiCat, json_action)
{
}

// STEP 0: Start the interaction
void Watch::begin()
{
  _HEA._lost_focus = false;
  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Watch::ongoing()
{

  // Check if Head alignment has been triggered
  if (_HEA._is_enacting_head_alignment)
  {
    _status ="move";
    _duration1 = millis() - _action_start_time;
    _action_end_time = 0;
    _step = INTERACTION_TERMINATE;
  }
  // If no Head alignment, manage the scan
  else if (_scan == nullptr)
  {
    if (millis() > _action_end_time)
    {
//      // Trigger the scan interaction
//      JSONVar json_action;
//      json_action["action"] = String(_action);
//      json_action["clock"] = _clock;
//      _scan = new Scan(_FLO, _HEA, _IMU, _WifiCat, json_action);
//      _scan -> begin();
//    }
//  }
//  // Execute the Scan interaction and then terminate
//  else
//  {
//    if (_scan -> update() == INTERACTION_TERMINATE)
//    {
////      delete _scan; _scan will be deleted by outcome()
////      _scan = nullptr;
      _duration1 = millis() - _action_start_time;
      _HEA.beginEchoAlignment();
      _step = INTERACTION_TERMINATE;
      _action_end_time = 0;
    }
  }
}

// Send the scan outcome

void Watch::outcome(JSONVar & outcome_object)
{

  if (_scan != nullptr)
  {
    _scan->outcome(outcome_object);
    delete _scan;
    _scan = nullptr;
  }
}

// Overrides the terminate() method to wait for end of echo scan
void Watch::terminate()
{
  // Turn on the color sensor led
  _FLO._CLR.begin_read();

  if (_action_end_time < millis() &&  !_FLO._is_enacting && !_HEA._is_enacting_head_alignment)
  {
    // Read the floor color and return true when done
    if (_FLO._CLR.end_read())
    {
      // When color has been read, proceed to step 3
      _step = INTERACTION_SEND;
      if (_HEA._lost_focus)
        _status ="lost";
    }
  }
}
