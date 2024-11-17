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
}

void Color::setup()
{
  // Initialize the white led and turn it off
  pinMode(Led_PIN, OUTPUT);
  digitalWrite(Led_PIN, LOW);

  // Initialize the sensor
  if (_tcs.begin())
  {
    Serial.println("-- Color sensor initialized");
    // tcs.disable();
    _tcs.setGain(TCS34725_GAIN_4X);
    // Set the integration time in the chip's register without adding an unnecessary delay to the getRawData() function
    _tcs.write8(TCS34725_ATIME, TCS34725_INTEGRATIONTIME_50MS);
    // tcs.setIntegrationTime(TCS34725_INTEGRATIONTIME_50MS);
    _is_initialized = true;
  }
  else
  {
    Serial.println("No color sensor TCS34725 found...");
    _is_initialized = false;
  }
}

// Turn on the led and starts the 50ms timer

void Color::begin_read()
{
  if (!_is_led_on)
  {
    digitalWrite(Led_PIN, HIGH);
    // tcs.enable();  // Turn the sensor on
    _read_start_time = millis();
    _is_led_on = true;
  }
}

// Wait for led on and then read the sensor and turn led of. Return true when done.
bool Color::end_read()
{
  if (_is_initialized)
  {
    if (millis() > _read_start_time + LED_ON_DURATION)
    {
      _tcs.getRawData(&_r, &_g, &_b, &_c);
      // tcs.disable();  // Turn the sensor off
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

  if (_is_initialized)
  {
    // uint16_t colorTemp = tcs.calculateColorTemperature_dn40(r, g, b, c);
    int red = 0;
    int green = 0;
    int blue = 0;

    if (_c > 0)
    {
      // Scale the RGB values based on clear and on calibration
      red = round((float)_r / (float)_c * 255.0 * WHITE_GREEN / WHITE_RED);
      green = round((float)_g / (float)_c * 255.0);  // Green is taken as reference because it is often the highest
      blue = round((float)_b / (float)_c * 255.0 * WHITE_GREEN / WHITE_BLUE);
    }

    JSONVar colorArray;
    colorArray["red"] = red;
    colorArray["green"] = green;
    colorArray["blue"] = blue;
    // colorArray["temp"] = colorTemp;
    colorArray["clear"] = _c;
    outcome_object["color"] = colorArray;
  }
}
