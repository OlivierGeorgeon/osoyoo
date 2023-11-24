/*
  Led.h - library to control the LEDs.
  Created Olivier Georgeon February 15 2023
  Released into the public domain
*/

#ifndef Led_h
#define Led_h

#define BLINK_PERIOD 100  // (ms) The period of blinking 10Hz
#define RED_LED_PIN 5
#define GREEN_LED_PIN 3
#define BLUE_LED_PIN 2


class Led
{
public:
  Led();
  void setup();
  void update();
  void color(int c);
private:
  unsigned long blink_time = 0;
  unsigned long cycle_count = 0;
  bool blink_on = true;
  float emotion_red = 0.;
  float emotion_green = 0.;
  float emotion_blue = 0.;
};

#endif