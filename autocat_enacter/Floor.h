/*
  Floor_change_retreat.h - library for Osoyoo car enacting floor change retreat behavior.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
#ifndef Floor_h
#define Floor_h

#include "Arduino.h"
#include "Wheel.h"
#include <Arduino_JSON.h>

#define RETREAT_DURATION 200
#define RETREAT_EXTRA_DURATION 100

class Floor
{
  public:
    Floor(Wheel& _OWM);  // The Wheel object is passed by reference to avoid creating another instance
    void update();
    int measureFloor();
    void extraDuration(int duration);
    bool _is_enacting;
    void outcome(JSONVar & outcome_object);
    int _floor_outcome;
    // String _debug_message;
  private:
    Wheel& _OWM;
    int _previous_measure_floor;
    unsigned long _floor_change_retreat_end_time;
};

#endif