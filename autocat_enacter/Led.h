/*
  Led.h - library to control the build in LED.
  Created Olivier Georgeon February 15 2023
  Released into the public domain
*/

#ifndef Led_h
#define Led_h

class Led
{
public:
  Led();
  void blink();
private:
  unsigned long blink_end_time = 0;
  bool blink_on = true;
};

#endif