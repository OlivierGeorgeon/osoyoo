#ifndef Head_Dist_h
#define Head_Dist_h
    
#include "Arduino.h"

class Head_Dist
{
    private:
    const byte TRIGGER_PIN = 30; // Broche TRIGGER
    const byte ECHO_PIN = 31;    // Broche ECHO

    /* Constants for the timeout */
    const unsigned long MEASURE_TIMEOUT = 25000UL; // 25ms = ~8m to 340m/s

    /* Speed of sound in air in mm/us */
    const float SOUND_SPEED = 340.0 / 1000;
    public:
    Head_Dist();
    void setup();
    float dist();
};

#endif
