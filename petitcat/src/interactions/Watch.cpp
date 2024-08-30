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
  _HEA._discontinuous = false; // Reset in outcome() to keep track of continuity across interactions
  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Watch::ongoing()
{

  // Check if Head alignment has been triggered
  if (_HEA._is_enacting_head_alignment)
  {
//    _status ="move";
    strcpy(_status, "move");
    _duration1 = millis() - _action_start_time;
    _action_end_time = 0;
    _step = INTERACTION_TERMINATE;
  }
  // If no Head alignment, manage the scan
  else if (_scan == nullptr)
  {
    if (millis() > _action_end_time)
    {
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
  if (!_HEA._discontinuous)
//    _status ="continuous";
    strcpy(_status, "continuous");
  _HEA._discontinuous = false;
}
