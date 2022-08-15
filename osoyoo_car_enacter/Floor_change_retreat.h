/*
  Floor_change_retreat.h - library for Osoyoo car enacting floor change retreat behavior.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
#ifndef Floor_change_retreat_h
#define Floor_change_retreat_h

#include "Arduino.h"
#include "Omny_wheel_motion.h"
#include <Arduino_JSON.h>

#define RETREAT_DURATION 200
#define RETREAT_EXTRA_DURATION 100

class Floor_change_retreat
{
  public:
    Floor_change_retreat(Omny_wheel_motion _OWM);
    void update();
    int measureFloor();
    void extraDuration(int duration);
    bool _is_enacting;
    void outcome(JSONVar & outcome_object);
    int _floor_outcome;
    // String _debug_message;
  private:
    Omny_wheel_motion _OWM;
    int _previous_measure_floor;
    unsigned long _floor_change_retreat_end_time;
};

#endif