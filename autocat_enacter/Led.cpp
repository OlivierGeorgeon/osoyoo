/*
  Led.cpp - library to control the build in LED.
  Created Olivier Georgeon February 15 2023
  Released into the public domain
*/

#include "Led.h"
#include "Arduino.h"

Led::Led()
{
  //blink_end_time = 0;
  //blink_on = true;
}

// Blink the LED with period 100ms
void Led::blink()
{
  // cycle_count++;
  if (millis() > blink_time + BLINK_PERIOD / 2)
  {
    blink_time = millis();
    // Serial.print("Cycle count:"); Serial.println(cycle_count);cycle_count = 0;  // For debug
    if (blink_on)
    {
      digitalWrite(LED_BUILTIN, HIGH);
      blink_on = false;
    }
    else
    {
      digitalWrite(LED_BUILTIN, LOW);
      blink_on = true;
    }
  }
}