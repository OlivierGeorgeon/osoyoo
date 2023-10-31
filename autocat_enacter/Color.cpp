/*
  Color.cpp - library to read the color sensor TCS34725.
  Created Olivier Georgeon March 24 2023
*/

#include "Color.h"
#include "Arduino.h"
#include "Robot_define.h"
#include <Wire.h>
#include <Adafruit_TCS34725.h>
#include <Arduino_JSON.h>

Color::Color()
{
  Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_24MS, TCS34725_GAIN_16X);
//  r = 0;
//  g = 0;
//  b = 0;
//  c = 0;
//  is_initialized = false;
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
    tcs.setGain(TCS34725_GAIN_4X);  // Gain x4 for better precision
    tcs.setIntegrationTime(TCS34725_INTEGRATIONTIME_50MS);
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

// Wait for led on and then read the sensor and turn led of. Return true when done.
bool Color::end_read()
{
  if (is_initialized)
  {
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

// Generate the outcome_object form previously read sensor
void Color::outcome(JSONVar & outcome_object)
{

  if (is_initialized)
  {
    // uint16_t colorTemp = tcs.calculateColorTemperature_dn40(r, g, b, c);
    int red = 0;
    int green = 0;
    int blue = 0;

    if (c > 0)
    {
      // Scale the RGB values based on clear and on calibration
      red = round((float)r / (float)c * 255.0 * WHITE_GREEN / WHITE_RED);
      green = round((float)g / (float)c * 255.0);  // Green is taken as reference because it is often the highest
      blue = round((float)b / (float)c * 255.0 * WHITE_GREEN / WHITE_BLUE);
    }

    JSONVar colorArray;
    colorArray["red"] = red;
    colorArray["green"] = green;
    colorArray["blue"] = blue;
    // colorArray["temp"] = colorTemp;
    colorArray["clear"] = c;
    outcome_object["color"] = colorArray;
  }
}
