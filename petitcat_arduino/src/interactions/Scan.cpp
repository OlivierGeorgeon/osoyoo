/*
  Scan.h - library for controlling the scan interaction
  Created by Olivier Georgeon, mai 29 2023
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
#include "Scan.h"

Scan::Scan(Floor& FCR, Head& HEA, Imu& IMU, WifiCat& WifiCat, JSONVar json_action) :
  Interaction(FCR, HEA, IMU, WifiCat, json_action)
{
}

// STEP 1: Start the interaction
void Scan::begin()
{
  _HEA._next_saccade_time = millis() + 3000;  // Inhibit HEA during the interaction (almost 3s if span = 10°)
  _HEA._is_enacting_head_alignment = false; // Stop current head alignment if any
  _min_ultrasonic_measure = NO_ECHO_DISTANCE;
  _head_angle = _HEA._head_angle;
  if (_head_angle > 0)
  {
    // If head is to the left, start from 80° and scan clockwise
    _head_angle = 80;
    _head_angle_span = -_span;
  }
  else
  {
    // If head is to the right, start from -80° and scan counterclockwise
    _head_angle = -80;
    _head_angle_span = _span;
  }
  _angle_min_ultrasonic_measure = _head_angle;
  _HEA.turnHead(_head_angle); // Start the scan right away
  _next_saccade_time = millis() + SACCADE_DURATION;
  _current_index = 0;
  _step = INTERACTION_ONGOING;
}

// STEP 2: Control the enaction
void Scan::ongoing()
{
  if (millis() > _next_saccade_time)
  {
    _current_ultrasonic_measure = _HEA.measureUltrasonicEcho();
    _next_saccade_time = millis() + SACCADE_DURATION;
    if (_current_ultrasonic_measure < _min_ultrasonic_measure)
    {
      _min_ultrasonic_measure = _current_ultrasonic_measure;
      _angle_min_ultrasonic_measure = _head_angle;
    }
    _sign_array.distances[_current_index] = _current_ultrasonic_measure;
    _sign_array.angles[_current_index] = _head_angle;
    Serial.println("Index: " + (String)_current_index + ", angle: " + (String)_head_angle + ", distance: "+ (String)_current_ultrasonic_measure);
    _current_index++;
    _head_angle += _head_angle_span;
    if (abs(_head_angle) > 90)
    { // The scan is over, move to the angle of the min measure
      _head_angle  = _angle_min_ultrasonic_measure;
      _head_angle_span = ALIGN_SACCADE_SPAN;  // reset saccade span for alignment
      Serial.println("Scan aligned at angle: " + String(_head_angle) + ", measure: " + String(_min_ultrasonic_measure));
      _HEA._next_saccade_time = millis() + ECHO_MONITOR_PERIOD; // Wait before monitoring again

      // Terminate the ongoing step
      _HEA.beginEchoAlignment();  // Trigger echo alignment
      _duration1 = millis() - _action_start_time;
      _duration2 = millis();
      _action_end_time = 0;
      _step = INTERACTION_TERMINATE;
    }
    _HEA.turnHead(_head_angle);
  }
}

// Send the scan outcome

void Scan::outcome(JSONVar & outcome_object)
{
  JSONVar echos;
  bool has_echo = false;
  for (int i = 0; i < _sign_array.size; i++)
  {
    if (_sign_array.distances[i] > 0 and _sign_array.distances[i]< 10000)
    {
      echos[String(_sign_array.angles[i])] = _sign_array.distances[i];
      has_echo = true;
    }
  }
  if (has_echo)
    outcome_object["echos"] = echos;
}
