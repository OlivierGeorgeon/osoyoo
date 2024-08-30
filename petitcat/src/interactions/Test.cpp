/*
  Test.h - The Test interaction can be used as a template to create new interactions
  Created by Olivier Georgeon, mai 15 2024
  released into the public domain
*/
#include "../wifi/WifiCat.h"
#include "../../Robot_define.h"
#include "../../Color.h"
#include "../../Floor.h"
#include "../../Head.h"
#include "../../Imu.h"
#include "../../Interaction.h"
#include "../../Action_define.h"
#include "Test.h"

Test::Test(Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action) :
  Interaction(FCR, HEA, IMU, WifiCat, json_action)
{
}

// STEP 0: Start the interaction
void Test::begin()
{
  // *** Add your own command here ***

  // Example: Turn the front left wheel backward (see available functions in Wheel.h)
  _FLO._OWM.frontLeftWheel(-SPEED);

  // Move on to next step
  _step = INTERACTION_ONGOING;
}

// STEP 1: Control the enaction
void Test::ongoing()
{
  // *** Implement your stop conditions here ***

  // Example: Stop after default duration
  if (_action_end_time < millis())
  {
    // Stop all the wheels
    _FLO._OWM.stopMotion();
    // Record the duration
    _duration1 = millis() - _action_start_time;
    // Move on to the next step
    _step = INTERACTION_TERMINATE;
  }
}

// STEP 3 Send the outcome
void Test::outcome(JSONVar & outcome_object)
{
  // ***  Add specific outcome for this interaction here ***

  // Example: add the field "test" with value 0 to the outcome string
  outcome_object["test"] = 0;

}
