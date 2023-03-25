/*
  Color.h - library to read the floor color using sensor TCS34725.
  Created Olivier Georgeon March 24 2023
*/

#ifndef Color_h
#define Color_h

#define Led_PIN 11
#include <Arduino_JSON.h>
#include <Adafruit_TCS34725.h>

class Color
{
  public:
    Color();
    void setup();
    void read();
    void outcome(JSONVar & outcome_object);
  private:
    Adafruit_TCS34725 tcs;
    bool is_initialized;
    float red;
    float green;
    float blue;
};

#endif