/*
  Floor_change_retreat - library for Osoyoo car enacting floor change retreat behavior.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
#include "Arduino.h"
#include "Floor_change_retreat.h"
#include "Omny_wheel_motion.h"
//#include <WiFiEsp.h>

#define sensor1   A4 // Left most sensor
#define sensor2   A3 // 2nd Left   sensor
#define sensor3   A2 // center sensor
#define sensor4   A1 // 2nd right sensor
#define sensor5   A0 // Right most sensor

Floor_change_retreat::Floor_change_retreat()
{
  Omny_wheel_motion _OWM;
  _is_enacting_floor_change_retreat = false;
  _previous_measure_floor = 0;
  _floor_change_retreat_end_time = 0;
}
bool Floor_change_retreat::update(int duration)
{
  // Detect change in the floor measure
  int current_measure_floor = measureFloor();
  int floor_change = current_measure_floor ^ _previous_measure_floor; // Bitwise XOR
  _previous_measure_floor = current_measure_floor;

  if (_is_enacting_floor_change_retreat)
  {
    if (millis() > _floor_change_retreat_end_time) {
      // End floor change retreat
      _OWM.stopMotion();
      Serial.println("End retreat at " + String(millis()));
      _is_enacting_floor_change_retreat = false;
    }
  }
  else // If is not enacting floor change retreat
  {
    if (floor_change != 0)
    {
      // Begin floor change retreat
      Serial.println("Floor change " + String(floor_change, BIN) + " Begin retreat at " + String(millis()));
      _is_enacting_floor_change_retreat = true;
      switch (floor_change) {
        case 0b10000:_OWM.setMotion(-150,-150,-50,-50);break; // back right
        case 0b11000:_OWM.setMotion(-150,-150,-50,-50);break; // back right
        case 0b00011:_OWM.setMotion(-50,-50,-150,-150);break; // back left
        case 0b00001:_OWM.setMotion(-50,-50,-150,-150);break; // back left
        default:_OWM.setMotion(-150,-150,-150,-150);break;
      }
      _floor_change_retreat_end_time = millis() + duration;
    }
  }
  return _is_enacting_floor_change_retreat;
}

int Floor_change_retreat::measureFloor()
{
  int s0 = !digitalRead(sensor1); // Left sensor
  int s1 = !digitalRead(sensor2);
  int s2 = !digitalRead(sensor3);
  int s3 = !digitalRead(sensor4);
  int s4 = !digitalRead(sensor5); // Right sensor
  int sensor_value=32;
  // from left to right: 1 when floor is dark and sensor's led is on
  sensor_value +=s0*16+s1*8+s2*4+s3*2+s4;
  //Serial.print("Flor sensor: ");
  //Serial.println(String(sensor_value, BIN));
  return sensor_value;
}
