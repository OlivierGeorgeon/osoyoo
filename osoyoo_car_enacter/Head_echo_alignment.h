/*
  Head_echo_alignment.h - library for Osoyoo car align head towards closest ultrasonic echo.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
#ifndef Head_echo_alignment_h
#define Head_echo_alignment_h
#include "Arduino.h"
#include <Servo.h>
#include <Arduino_JSON.h>

#define SACCADE_DURATION 150 // 150 Servo specification speed is 120ms/60°
#define SACCADE_SPAN     5
#define ECHO_MONITOR_PERIOD 500 // The period for checking whether to trigger head alignment
#define ECHO_MONITOR_VARIATION 50 // the measure threshold to trigger head alignment

struct significant_array {
        // Struct to store the angles and the corresponding measures,
        // and booleans to indicate if the measure are significant
        int distances[180/SACCADE_SPAN]{0};
        int angles[180/SACCADE_SPAN]{0};
        bool sign[180/SACCADE_SPAN]{false};
        int size = 180/SACCADE_SPAN;
    };
class Head_echo_alignment
{
  public:
    Head_echo_alignment();
    void setup();
    void beginEchoAlignment();
    void beginEchoScan();
    void update();
    int measureUltrasonicEcho();
    void outcome(JSONVar & outcome_object);
    void turnHead(int head_angle);
    int _head_angle;
    bool _is_enacting_head_alignment;
    bool _is_enacting_echo_scan;
    unsigned long _next_saccade_time;
  private:
    Servo _head;
    int _penultimate_ultrasonic_measure;
    int _previous_ultrasonic_measure;
    int _min_ultrasonic_measure;
    int _angle_min_ultrasonic_measure;
    int _head_angle_span;
    int _echo_alignment_step;
    significant_array _sign_array;
    int _current_index;
};

#endif