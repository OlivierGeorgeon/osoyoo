/*
  Led.h - library to control the build in LED.
  Created Olivier Georgeon February 15 2023
  Released into the public domain
*/

#ifndef Led_h
#define Led_h

#define BLINK_PERIOD 100  // (ms) The period of blinking 10Hz

class Led
{
public:
  Led();
  void blink();
private:
  unsigned long blink_time = 0;
  unsigned long cycle_count = 0;
  bool blink_on = true;
};

#endif