/*
  Color.h - library to read the floor color using sensor TCS34725.
  Created Olivier Georgeon March 24 2023
*/

#ifndef Color_h
#define Color_h

#define Led_PIN 53         // Pin number
#define LED_ON_DURATION 200  // Give time to immobilize 50  // (ms) led on before reading the color
#include <Arduino_JSON.h>
#include <Adafruit_TCS34725.h>

class Color
{
  public:
    Color();
    void setup();
    void begin_read();
    bool end_read();
    void outcome(JSONVar & outcome_object);
  private:
    Adafruit_TCS34725 _tcs; // Integration time and gain will be set by setup()
    bool _is_initialized = false;
    uint16_t _r = 0;
    uint16_t _g = 0;
    uint16_t _b = 0;
    uint16_t _c = 0;
    unsigned long _read_start_time;
    bool _is_led_on = false;
};

#endif