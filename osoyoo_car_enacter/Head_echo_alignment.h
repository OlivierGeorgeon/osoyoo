/*
  Head_echo_alignment.h - library for Osoyoo car align head towards closest ultrasonic echo.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
#ifndef Head_echo_alignment_h
#define Head_echo_alignment_h
#include "Arduino.h"
#include <Servo.h>

#define SACCADE_DURATION 150 // Servo specification speed is 120ms/60°
#define SACCADE_SPAN     10

class Head_echo_alignment
{
  public:
    Head_echo_alignment();
    void setup();
    void begin();
    bool update();
    int measureUltrasonicEcho();
    String outcome();
  private:
    Servo _head;
    bool _is_enacting_head_alignment;
    int _penultimate_ultrasonic_measure;
    int _previous_ultrasonic_measure;
    unsigned long _next_saccade_time;
    int _head_angle;
    int _head_angle_span;
};

#endif