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
  red = 0;
  green = 0;
  blue = 0;
  is_initialized = false;
}

void Color::setup()
{
  // Initialize the white led and turn it off
  pinMode(Led_PIN, OUTPUT);
  digitalWrite(Led_PIN, LOW);

  // Initialize the sensor
  if (tcs.begin()) {
    Serial.println("Color sensor initialized");
    is_initialized = true;
  } else {
    Serial.println("No TCS34725 found ... check your connections");
    is_initialized = false;
    //while (1); // halt!
  }
}

// Read the sensor
void Color::read()
{
  if (is_initialized){
    // Switch the LED on
    digitalWrite(Led_PIN, HIGH);

    // TODO : don't block the loop
    delay(30);  // takes 50ms to read

    tcs.getRGB(&red, &green, &blue);

    digitalWrite(Led_PIN, LOW);
  }
}

void Color::outcome(JSONVar & outcome_object)
{

  if (is_initialized){
    // Scale the measure
    red = constrain(red, 90, 190);
    red = map(red, 90, 190, 0, 255);
    green = constrain(green, 90, 130);
    green = map(green, 90, 130, 0, 255);
    blue = constrain(blue, 80, 120);
    blue = map(blue, 80, 120, 0, 255);

    outcome_object["red"] = (int)red;
    outcome_object["green"] = (int)green;
    outcome_object["blue"] = (int)blue;

    // TODO Test that
    JSONVar colorArray;
    colorArray["red"] = (int)red;
    colorArray["green"] = (int)green;
    colorArray["blue"] = (int)blue;
    outcome_object["colors"] = colorArray;

//  JSONVar colorTest = outcome_object.createNestedObject();
//  colorTest["red"] = (int)red;
//  colorTest["green"] = (int)green;
//  colorTest["blue"] = (int)blue;
  }
}
