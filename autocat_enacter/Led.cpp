/*
  Led.h - library to control the build in LED.
  Created Olivier Georgeon February 15 2023
  Released into the public domain
*/

#include "Led.h"
#include "Arduino.h"

Led::Led()
{
  blink_end_time = 0;
  blink_on = true;
}

// Blink the LED with period 100ms
void Led::blink()
{
  if (millis() > blink_end_time){
    if (blink_on) {
      digitalWrite(LED_BUILTIN, HIGH);
      blink_on = false;
    }else {
      digitalWrite(LED_BUILTIN, LOW);
      blink_on = true;
    }
    blink_end_time = millis() + 50;
  }
}