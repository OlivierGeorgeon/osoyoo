/*
  Color.cpp - library to read the color sensor TCS34725.
  Created Olivier Georgeon March 24 2023
*/

#include "Color.h"
#include "Arduino.h"
#include <Wire.h>
#include <Adafruit_TCS34725.h>
#include <Arduino_JSON.h>

Color::Color()
{
  Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_24MS, TCS34725_GAIN_16X);
  r = 0;
  g = 0;
  b = 0;
  c = 0;
  is_initialized = false;
}

void Color::setup()
{
  // Initialize the white led and turn it off
  pinMode(Led_PIN, OUTPUT);
  digitalWrite(Led_PIN, LOW);

  // Initialize the sensor
  if (tcs.begin())
  {
    Serial.println("Color sensor initialized");
    is_initialized = true;
  }
  else
  {
    Serial.println("No TCS34725 found ... check your connections");
    is_initialized = false;
    //while (1); // halt!
  }
}

// Turn on the led and starts the 50ms timer

void Color::begin_read()
{
  if (!_is_led_on)
  {
    digitalWrite(Led_PIN, HIGH);
    _read_start_time = millis();
    _is_led_on = true;
  }
}

// Read the sensor
bool Color::end_read()
{
  if (is_initialized)
  {
    // Switch the LED on
    // digitalWrite(Led_PIN, HIGH);

    // delay(50);  // takes 50ms to read
    if (millis() > _read_start_time + LED_ON_DURATION)
    {
      tcs.getRawData(&r, &g, &b, &c);
      digitalWrite(Led_PIN, LOW);
      _is_led_on = false;
      return true;
    }
    else
      return false;
  }
  // No color sensor then always return true
  else
    return true;
}

void Color::outcome(JSONVar & outcome_object)
{

  if (is_initialized)
  {
    // Scale the measure
    //red = constrain(red, 90, 190);
    //red = map(red, 90, 190, 0, 255);
    //green = constrain(green, 90, 130);
    //green = map(green, 90, 130, 0, 255);
    //blue = constrain(blue, 80, 120);
    //blue = map(blue, 80, 120, 0, 255);

    uint16_t colorTemp = tcs.calculateColorTemperature_dn40(r, g, b, c);
    int red;
    int green;
    int blue;

    if (c == 0)
      red = green = blue = 0;
    else
    {
      red = (int)((float)r / (float)c * 255.0);
      green = (int)((float)g / (float)c * 255.0);
      blue = (int)((float)b / (float)c * 255.0);
    }

    JSONVar colorArray;
    colorArray["red"] = red;
    colorArray["green"] = green;
    colorArray["blue"] = blue;
    colorArray["temp"] = colorTemp;
    colorArray["clear"] = c;
    outcome_object["color"] = colorArray;
  }
}
