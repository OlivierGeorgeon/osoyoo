/*
  Head_echo_alignment.h - library for Osoyoo car align head towards closest ultrasonic echo.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
#include "Arduino.h"
#include "Robot_define.h"
#include "head_echo_alignment.h"
#include <Servo.h>

//#define SERVO_PIN   13  //servo connect to D5
#define Echo_PIN    31  // Ultrasonic Echo pin connect to A5
#define Trig_PIN    30  // Ultrasonic Trig pin connect to A4

Head_echo_alignment::Head_echo_alignment()
{
  //Servo _head;
  _is_enacting_head_alignment = false;
  _is_enacting_echo_scan = false;
  _penultimate_ultrasonic_measure = 0;
  _previous_ultrasonic_measure = 1;
  _min_ultrasonic_measure = 0;
  _next_saccade_time = 0;
  _head_angle = 0;
  _head_angle_span = SACCADE_SPAN;
}

void Head_echo_alignment::setup()
{
  // init HC-SR04 ultrasonic Echo sensor
  pinMode(Trig_PIN, OUTPUT);
  pinMode(Echo_PIN,INPUT);
  digitalWrite(Trig_PIN,LOW);
  // init servo
  _head.attach(ROBOT_SERVO_PIN);
  turnHead(0); // Head straight ahead
  //_head.write(_head_angle + 90);
  //Serial.println("HEA initialized");
}

void Head_echo_alignment::beginEchoAlignment()
{
  _is_enacting_head_alignment = true;
  _penultimate_ultrasonic_measure = 1;  // Reinitialize previous measures so it will not ...
  _previous_ultrasonic_measure = 10001; // ... believe that the next measure is a minimum
  _head_angle_span = SACCADE_SPAN;
  turnHead(_head_angle - _head_angle_span);
  _next_saccade_time = millis() + SACCADE_DURATION;
}
void Head_echo_alignment::beginEchoScan()
{
  _is_enacting_head_alignment = false; // Stop current head alignment if any
  _is_enacting_echo_scan = true;
  _min_ultrasonic_measure = 10000;
  if (_head_angle > 0) {
    // If head is to the left, start from 90° and scan every 20° clockwise
    _angle_min_ultrasonic_measure = 90;
    _head_angle_span = -SACCADE_SPAN * 2; // saccade 20°
  } else {
    // If head is to the right, start from -90° and scan every 20° counterclockwise
    _angle_min_ultrasonic_measure = -90;
    _head_angle_span = SACCADE_SPAN * 2;
  }
  turnHead(_angle_min_ultrasonic_measure); // Start the scan right away
  _next_saccade_time = millis() + SACCADE_DURATION;
}

void Head_echo_alignment::update()
{
  if (millis() > _next_saccade_time )
  {
    if (_is_enacting_head_alignment)
    {
      _next_saccade_time = millis() + SACCADE_DURATION;
      int current_ultrasonic_measure = measureUltrasonicEcho();
      //if (current_ultrasonic_measure > 0) // Ignore measure 0. Will measure again on the next loop
      //{
        if (_previous_ultrasonic_measure > current_ultrasonic_measure ) {
          // Moving closer
          if ((_head_angle <= -90) || (_head_angle >= 90)) {
            // If reached the max then the min is here
            _min_ultrasonic_measure = current_ultrasonic_measure;
            Serial.println("Aligned at edge angle " + String(_head_angle) + " measure " + String(_min_ultrasonic_measure));
            _is_enacting_head_alignment = false;
            _next_saccade_time = millis() + ECHO_MONITOR_PERIOD; // Wait before monitoring again
          } else {
            turnHead(_head_angle += _head_angle_span);
          //if ((_head_angle > -80) && (_head_angle < 80)) {
          //  _head_angle += _head_angle_span;
          //  _head.write(_head_angle + 90);
          }
        } else {
          // moving away, reverse movement
          _head_angle_span = - _head_angle_span;
          _head_angle += _head_angle_span; // may reach -100° or 100° but ...
          turnHead(_head_angle);           // ... turnHead() sets it back to -90° or 90°
           // Passed the minimum, stop
          if (_penultimate_ultrasonic_measure > _previous_ultrasonic_measure ) {
            _min_ultrasonic_measure = _previous_ultrasonic_measure;
            Serial.println("Aligned at angle " + String(_head_angle) + " measure " + String(_min_ultrasonic_measure));
            _is_enacting_head_alignment = false;
            _next_saccade_time = millis() + ECHO_MONITOR_PERIOD; // Wait before monitoring again
            //_head_angle_span = - _head_angle_span;
          }
        }
      //}
      _penultimate_ultrasonic_measure = _previous_ultrasonic_measure;
      _previous_ultrasonic_measure = current_ultrasonic_measure;
    }
    else if (_is_enacting_echo_scan)
    {
      int current_ultrasonic_measure = measureUltrasonicEcho();
      _next_saccade_time = millis() + SACCADE_DURATION;
      // Ignore measure 0
      if (current_ultrasonic_measure > 0 && current_ultrasonic_measure < _min_ultrasonic_measure){
        _min_ultrasonic_measure = current_ultrasonic_measure;
        _angle_min_ultrasonic_measure = _head_angle;
      }
      _head_angle += _head_angle_span;
      //_head.write(_head_angle + 90);
      if (abs(_head_angle) > 90){ // The scan is over, move to the angle of the min measure
        _is_enacting_echo_scan = false;
        _head_angle  = _angle_min_ultrasonic_measure;
        // turnHead(_angle_min_ultrasonic_measure);
        Serial.println("Aligned to closest angle " + String(_head_angle) + " measure " + String(_min_ultrasonic_measure));
        _next_saccade_time = millis() + ECHO_MONITOR_PERIOD; // Wait before monitoring again
      }
      turnHead(_head_angle);
    }
    else // Watch for variation in ultrasonic measure to trigger alignment
    {
      _next_saccade_time = millis() + ECHO_MONITOR_PERIOD;
      int current_ultrasonic_measure = measureUltrasonicEcho();

      if (current_ultrasonic_measure > 0 && abs(current_ultrasonic_measure - _min_ultrasonic_measure) > ECHO_MONITOR_VARIATION) {
        Serial.println("Trigger head alignment from variation " + String(current_ultrasonic_measure - _min_ultrasonic_measure));
        beginEchoAlignment();
      }
    }
  }
}

void Head_echo_alignment::outcome(JSONVar & outcome_object)
{
  outcome_object["head_angle"] = _head_angle;
  outcome_object["echo_distance"] = _min_ultrasonic_measure;
}

void Head_echo_alignment::turnHead(int head_angle)
{
  _head_angle = constrain(head_angle, -90, 90);
  // if (_head_angle > 90) _head_angle = 90;
  // if (_head_angle < -90) _head_angle = -90;
  _head.write(_head_angle + 90);
}

int Head_echo_alignment::measureUltrasonicEcho()
{
  long echo_distance;
  digitalWrite(Trig_PIN,LOW);
  delayMicroseconds(5);
  digitalWrite(Trig_PIN,HIGH);
  delayMicroseconds(15);
  digitalWrite(Trig_PIN,LOW);
  echo_distance = pulseIn(Echo_PIN,HIGH, 10000);  // Timeout 10 milliseconds. It blocks the main loop!
  echo_distance = (int)(echo_distance * 0.1657);  // How far away is the object in mm
  if (echo_distance == 0) echo_distance = 10000;  // Zero counts for far away
  Serial.println("Angle " +String(_head_angle) + " measure " + String(echo_distance));
  return echo_distance;
}