/*
  Floor_change_retreat - library for Osoyoo car enacting floor change retreat behavior.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/

#include "Action_define.h"
#include "Arduino.h"
#include "Floor.h"
#include "Wheel.h"

#define sensor1   A4 // Left most sensor
#define sensor2   A3 // 2nd Left sensor
#define sensor3   A2 // center sensor
#define sensor4   A1 // 2nd right sensor
#define sensor5   A0 // Right most sensor

Floor::Floor()
{
}

void Floor::setup()
{
  _OWM.setup();
  _CLR.setup();
}

int Floor::update(int interaction_direction)
{
  // Detect change in the floor measure
  int current_measure_floor = measureFloor();
  int floor_change = current_measure_floor ^ _previous_measure_floor; // Bitwise XOR
  _previous_measure_floor = current_measure_floor;

  // If is not already retreating then monitor the floor luminosity signal

  if (!_is_retreating)
  {
    // Watch whether the floor has changed
    if (floor_change != 0)
    {
      // digitalWrite(LED_BUILTIN, HIGH); // for debug
      // Serial.println("Floor change " + String(floor_change, BIN) + " Begin retreat at " + String(millis()));

      // Convert the five luminosity-sensor signal to a two-bit code

      _is_retreating = true;
      if (floor_change == 0b00100)
        _floor_outcome = B11;
      else if ((floor_change & 0b00011) == 0)
        _floor_outcome = B10;
      else if ((floor_change & 0b11000) == 0)
        _floor_outcome = B01;
      else
        _floor_outcome = B11;

      // Trigger the appropriate retreat movement

      _retreat_end_time = millis() + RETREAT_DURATION * 2;  // * 5;
      // If was swiping left then retreat right for 400ms
      if (interaction_direction == DIRECTION_LEFT)
        _OWM.retreatRight();
      // If was swiping right then retreat left for 400ms
      else if (interaction_direction == DIRECTION_RIGHT)
        _OWM.retreatLeft();
      else
      {
        _retreat_end_time = millis() + RETREAT_DURATION;
        // If was moving backward then retreat front for 200ms
        if (interaction_direction == DIRECTION_BACK)
          _OWM.retreatFront();
        // If was moving forward or turning
        else
        {
          // If line in front then retreat strait for 200ms
          if (_floor_outcome == B11)
            _OWM.retreatStrait();
          else
          {
            _retreat_end_time = millis() + RETREAT_DURATION * 2;
            // if line on the left then retreat right for 400ms
            if (_floor_outcome == B10)
              _OWM.retreatRight();
            // if line on the right then retreat left for 400ms
            else
              _OWM.retreatLeft();
          }
        }
      // _debug_message += String(millis()) + ": floor changed. ";
      }
    }
  }

  // If currently retreating then monitor the time out and more flore change

  if (_is_retreating)
  {
    // When the floor changes when retreating sideways, postpone the end time because robot may still be on the line
    if (floor_change != 0 && _floor_outcome != B11)
      _retreat_end_time = max(millis() + RETREAT_DURATION, _retreat_end_time);

    // When the retreat time has elapsed, terminate the retreat
    if (millis() > _retreat_end_time)
    {
      // Stop the retreat
      _OWM.stopMotion();
      // _debug_message += String(millis()) + ": end retreat. ";
      _is_retreating = false;
    }
  }
  return _floor_outcome;
}

void Floor::extraDuration(int duration)
{
  _retreat_end_time += duration;
}

int Floor::measureFloor()
{
  int s0 = !digitalRead(sensor1); // Left sensor
  int s1 = !digitalRead(sensor2);
  int s2 = !digitalRead(sensor3);
  int s3 = !digitalRead(sensor4);
  int s4 = !digitalRead(sensor5); // Right sensor
  // from left to right: 1 when floor is dark and sensor's led is on
  int sensor_value = s0*16+s1*8+s2*4+s3*2+s4;
  //Serial.print("Flor sensor: ");
  //Serial.println(String(32 + sensor_value, BIN)); // Begin with "1" so we can see all the zeros
  return sensor_value;
}

void Floor::outcome(JSONVar & outcome_object)
{
  outcome_object["floor"] = _floor_outcome;
  _CLR.outcome(outcome_object);
  // outcome_object["debug"] = _debug_message;
  // _debug_message = "";
  // _floor_outcome = 0;  // Reset at the beginning of the interaction. Not here because lost if outcome string lost
}
