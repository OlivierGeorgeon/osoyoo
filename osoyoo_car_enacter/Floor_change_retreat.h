/*
  Floor_change_retreat.h - library for Osoyoo car enacting floor change retreat behavior.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
#ifndef Floor_change_retreat_h
#define Floor_change_retreat_h

#include "Arduino.h"
#include "Omny_wheel_motion.h"

#define RETREAT_DURATION_IMMOBILE 200
#define RETREAT_DURATION_REVERSE  300

class Floor_change_retreat
{
  public:
    Floor_change_retreat();
    bool update(int duration);
    int measureFloor();
  private:
    Omny_wheel_motion _OWM;
    bool _is_enacting_floor_change_retreat;
    int _previous_measure_floor;
    unsigned long _floor_change_retreat_end_time;
};

#endif