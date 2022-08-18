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

//#define SERVO_PIN   13  //servo connect to D5. Now defined in Robot_define.h
#define Echo_PIN    31  // Ultrasonic Echo pin connect to A5
#define Trig_PIN    30  // Ultrasonic Trig pin connect to A4

#define SACCADE_DURATION 150      // (ms) Servo specification speed is 120ms/60°
#define ALIGN_SACCADE_SPAN 10     // (degrees)
//#define SCAN_SACCADE_SPAN 40      // (degrees) For full scan followed by head alignment
#define SCAN_SACCADE_SPAN 10   // (degrees) For complete-scan
#define ECHO_MONITOR_PERIOD 500   // (ms) The period for checking whether to trigger head alignment
#define ECHO_MONITOR_VARIATION 50 // (mm) The measure threshold to trigger head alignment

struct significant_array {
        // Struct to store the angles and the corresponding measures,
        // and booleans to indicate if the measure are significant
        int distances[180/SCAN_SACCADE_SPAN]{0};
        int angles[180/SCAN_SACCADE_SPAN]{0};
        bool sign[180/SCAN_SACCADE_SPAN]{false};
        int size = 180/SCAN_SACCADE_SPAN;
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
    void outcome_complete(JSONVar & outcome_object);
    void turnHead(int head_angle);
    int head_direction(int x, int y);
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