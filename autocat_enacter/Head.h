/*
  Head_echo_alignment.h - library for Osoyoo car align head towards closest ultrasonic echo.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/

#ifndef Head_h
#define Head_h
#include "Arduino.h"
#include <Servo.h>
#include <Arduino_JSON.h>

#define Echo_PIN    31  // Ultrasonic Echo pin connect to A5
#define Trig_PIN    30  // Ultrasonic Trig pin connect to A4

#define SACCADE_DURATION 150      // (ms) Servo specification speed is 120ms/60°
#define ALIGN_SACCADE_SPAN 10     // (degrees)
#define SCAN_SACCADE_SPAN 40      // (degrees) For full scan followed by head alignment
// #define SCAN_SACCADE_SPAN 10   // (degrees) For complete-scan
#define SCAN_SIZE 5               // Size of the array of scans
// #define SCAN_SIZE 18           // Size of the array of scans for complete scan
#define ECHO_MONITOR_PERIOD 50    // 500 (ms) The period for checking whether to trigger head alignment
#define ECHO_MONITOR_VARIATION 50 // (mm) The measure threshold to trigger head alignment
#define NO_ECHO_DISTANCE 10000    // (mm) Default distance when no echo

class Head
{
  public:
    Head();
    void setup();
    void beginEchoAlignment();
    void update();
    int measureUltrasonicEcho();
    void outcome(JSONVar & outcome_object);
    void turnHead(int head_angle);
    int head_direction(int x, int y);
    int get_ultrasonic_measure();
    int _head_angle;
    bool _is_enacting_head_alignment;
    bool _is_enacting_echo_scan;
    unsigned long _next_saccade_time;
    bool _discontinuous = false;
  private:
    Servo _head;
    int _penultimate_ultrasonic_measure = 1;
    int _previous_ultrasonic_measure = NO_ECHO_DISTANCE;
    int _current_ultrasonic_measure = NO_ECHO_DISTANCE;
    int _min_ultrasonic_measure = NO_ECHO_DISTANCE;
    int _angle_min_ultrasonic_measure;
    int _head_angle_span;
    int _echo_alignment_step;
};

#endif