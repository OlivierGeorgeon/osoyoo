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
  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Watch::ongoing()
{

  // Check if Head alignment has been triggered
  if (_HEA._is_enacting_head_alignment)
  {
    _status ="move";
    _duration1 = millis()- _action_start_time;
    _action_end_time = 0;
    _step = INTERACTION_TERMINATE;
  }
  // If no Head alignment, check whether duration has elapsed
  else if ((_action_end_time < millis() )) // || _IMU.get_impact_rightwards() > 0)
  {
    // Trigger echo scan
    _HEA.beginEchoScan();
    _duration1 = millis()- _action_start_time;
    _step = INTERACTION_TERMINATE;
    _action_end_time = 0;
  }
}

// Overrides the terminate() method to wait for end of echo scan
void Watch::terminate()
{
  // Turn on the color sensor led
  _FCR._CLR.begin_read();

  if (_action_end_time < millis() &&  !_FCR._is_enacting && !_HEA._is_enacting_echo_scan && !_HEA._is_enacting_head_alignment)
  {
    // Read the floor color and return true when done
    if (_FCR._CLR.end_read())
      // When color has been read, proceed to step 3
      _step = INTERACTION_SEND;
  }
}
