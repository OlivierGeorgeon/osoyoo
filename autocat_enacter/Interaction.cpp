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

Interaction::Interaction(
  Color& CLR,
  Floor& FCR,
  Head& HEA,
  Imu& IMU,
  WifiCat& WifiCat,
  unsigned long& action_end_time,
  int& interaction_step,
  String& status,
  char& action,
  int& clock,
  unsigned long& duration1,
  unsigned long& action_start_time
  ) :
  _CLR(CLR), _FCR(FCR), _HEA(HEA), _IMU(IMU), _WifiCat(WifiCat),_action_end_time(action_end_time),
  _interaction_step(interaction_step), _status(status), _action(action), _clock(clock), _duration1(duration1),
  _action_start_time(action_start_time)
{
}

// Wait for the interaction to terminate and proceed to Step 3
// Wait for Floor change retreat completed otherwise the wifi send interfers with the retreat
// Wait for Head alignment completed otherwise the head signal sent comes from before the interaction
// Warning: in some situations, the head alignment may take quite long
void Interaction::step2()
{
  if (_action_end_time < millis() &&  !_FCR._is_enacting && !_HEA._is_enacting_head_alignment /*&& !HECS._is_enacting_echo_scan*/)
  {
    _CLR.read();
    _interaction_step = 3;
  }
}

// Proceed with the enaction of the interaction
void Interaction::update()
{
  // STEP 2: Enacting the termination of the interaction: Floor change retreat, Stabilisation time
  // Wait for Floor change retreat completed otherwise the wifi send interfers with the retreat
  // Wait for Head alignment completed otherwise the head signal sent comes from before the interaction
  // Warning: in some situations, the head alignment may take quite long
  if (_interaction_step == 2)
  {
    if (_action_end_time < millis() &&  !_FCR._is_enacting && !_HEA._is_enacting_head_alignment /*&& !HECS._is_enacting_echo_scan*/)
    {
      // Read the floor color
      _CLR.read();
      // Proceed to step 3
      _interaction_step = 3;
    }
  }
  // STEP 3: Ending the interaction:
  // Send the outcome and go back to Step 0
  if (_interaction_step == 3)
  {
    // Compute the outcome message
    JSONVar outcome_object;
    outcome_object["status"] = _status;
    outcome_object["action"] = String(_action);
    outcome_object["clock"] = _clock;
    _CLR.outcome(outcome_object);
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

    // Ready to begin a new interaction
    _interaction_step = 0;
  }
}
