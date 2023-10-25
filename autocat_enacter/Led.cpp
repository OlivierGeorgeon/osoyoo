/*
  Led.cpp - library to control the build in LED.
  Created Olivier Georgeon February 15 2023
  Released into the public domain
*/

#include "Led.h"
#include "Arduino.h"

Led::Led()
{
}

// Initialize the led pins
void Led::setup()
{
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(BLUE_LED_PIN, OUTPUT);
}

// Blink the LED with period 100ms
void Led::blink()
{
  // cycle_count++;
  // Blink the builtin led
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

  // Pulse the emotion led
  //unsigned long currentTime = millis();  // Get the current time in milliseconds
  float sinValue = sin(0.00628 * millis());  // Calculate the sine value (* 2 * PI / period)

  analogWrite(RED_LED_PIN, (sinValue + 1.) * 100. * emotion_red);     // [0,200] Set the LED brightness using PWM
  analogWrite(GREEN_LED_PIN, (sinValue + 1.) * 105. * emotion_green); // [0,210]
  analogWrite(BLUE_LED_PIN, (sinValue + 1.) * 127.5 * emotion_blue);  // [0,255]
}

void Led::color(int c)
{
  // Off
  if (c == 0)
  {
    emotion_red = 0.;
    emotion_green = 0.;
    emotion_blue = 0.;
  }
  // Relaxed: White
  if (c == 1)
  {
    emotion_red = 1.;
    emotion_green = 1.;
    emotion_blue = 1.;
  }
  // Happy: Green
  if (c == 2)
  {
    emotion_red = 0.;
    emotion_green = 1.;
    emotion_blue = 0.;
  }
  // Sad: Blue
  if (c == 3)
  {
    emotion_red = 0.;
    emotion_green = 0.;
    emotion_blue = 1.;
  }
  // Angry: Red
  if (c == 4)
  {
    emotion_red = 1.;
    emotion_green = 0.;
    emotion_blue = 0.;
  }
}
