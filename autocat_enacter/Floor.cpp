/*
  Floor_change_retreat - library for Osoyoo car enacting floor change retreat behavior.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
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

int Floor::update()
{
  // Detect change in the floor measure
  int current_measure_floor = measureFloor();
  int floor_change = current_measure_floor ^ _previous_measure_floor; // Bitwise XOR
  _previous_measure_floor = current_measure_floor;

  // If is not already retreating
  if (!_is_retreating)
  {
    // Watch whether the floor has changed
    if (floor_change != 0)
    {
      // digitalWrite(LED_BUILTIN, HIGH); // for debug
      // Start the retreat
      // Serial.println("Floor change " + String(floor_change, BIN) + " Begin retreat at " + String(millis()));
      _is_retreating = true;
      switch (floor_change)
      {
        case 0b10000:
        case 0b11000:
        case 0b01000:
        case 0b11100:
        case 0b01100:
        case 0b10100:
          // Retreat right
          _OWM.retreatRight();
          //_OWM.setMotion(-150,-150,-50,-50);
          _floor_outcome = B10;
          _retreat_end_time = millis() + RETREAT_DURATION + 2* RETREAT_EXTRA_DURATION;
          break;
        case 0b00111:
        case 0b00101:
        case 0b00110:
        case 0b00011:
        case 0b00010:
        case 0b00001:
          // Retreat left
          _OWM.retreatLeft();
          _floor_outcome = B01;
          _retreat_end_time = millis() + RETREAT_DURATION + 2 * RETREAT_EXTRA_DURATION;
          break;
        default:
          // Retreat straight
          _OWM.retreatStrait();
          _floor_outcome = B11;
          _retreat_end_time = millis() + RETREAT_DURATION;
          break;
      }
      // _debug_message += String(millis()) + ": floor changed. ";
    }
  }
  // IF currently retreating
  if (_is_retreating)
  {
    // Check whether the retreat time has elapsed
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
  // TODO Must not reread the color because the led is off
  _CLR.outcome(outcome_object);
  // outcome_object["debug"] = _debug_message;
  // _debug_message = "";
  // _floor_outcome = 0;  // Reset at the beginning of the interaction. Not here because lost if outcome string lost
}
