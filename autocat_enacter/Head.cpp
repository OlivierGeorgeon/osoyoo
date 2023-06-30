/*
  Head_echo_alignment.h - library for Osoyoo car align head towards closest ultrasonic echo.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
#include "Arduino.h"
#include "Robot_define.h"
#include "Head.h"
#include <Servo.h>

Head::Head()
{
  _is_enacting_head_alignment = false;
  _is_enacting_echo_scan = false;
  _penultimate_ultrasonic_measure = 0;
  _previous_ultrasonic_measure = 1;
  _min_ultrasonic_measure = 0;
  _next_saccade_time = 0;
  _head_angle = 0;
  _head_angle_span = ALIGN_SACCADE_SPAN;
}

void Head::setup()
{
  // init HC-SR04 ultrasonic Echo sensor
  pinMode(Trig_PIN, OUTPUT);
  pinMode(Echo_PIN,INPUT);
  digitalWrite(Trig_PIN,LOW);
  // init servo
  _head.attach(ROBOT_SERVO_PIN);
  turnHead(0); // Head straight ahead
  //Serial.println("HEA initialized");
  _head_angle_span = ALIGN_SACCADE_SPAN;
}

void Head::beginEchoAlignment()
{
  _is_enacting_head_alignment = true;
//  _penultimate_ultrasonic_measure = 1;  // Reinitialize previous measures so it will not ...
//  _previous_ultrasonic_measure = NO_ECHO_DISTANCE; // ... believe that the next measure is a minimum
//  _current_ultrasonic_measure = NO_ECHO_DISTANCE;
  _echo_alignment_step = 0;
  _head_angle_span =  -_head_angle_span;  // Inverse the movement to track moving objects more easily
  _next_saccade_time = millis() + SACCADE_DURATION;
}

void Head::update()
{
  if (millis() > _next_saccade_time )
  {
    if (_is_enacting_head_alignment)
    {
      _echo_alignment_step++;
      _next_saccade_time = millis() + SACCADE_DURATION;
      _current_ultrasonic_measure = measureUltrasonicEcho();
      Serial.println("Step: " + String(_echo_alignment_step) + ", Angle: " +String(_head_angle) + ", measure: " + String(_current_ultrasonic_measure));
      if (_previous_ultrasonic_measure > _current_ultrasonic_measure )
      // The echo is closer
      {
        if ((_head_angle <= -90) || (_head_angle >= 90))
        // The head reached the limit angle
        {
          if (_echo_alignment_step > 1)
          // The echo is closer after several steps then the min distance is on the limit angle
          {
            _min_ultrasonic_measure = _current_ultrasonic_measure;
            Serial.println("Aligned at limit angle: " + String(_head_angle) + ", measure " + String(_min_ultrasonic_measure));
            _is_enacting_head_alignment = false;
            _next_saccade_time = millis() + ECHO_MONITOR_PERIOD; // Wait before monitoring again
          }
          else
          // First step on the limit angle: apply the saccade towards the center
          {
            _head_angle_span = ALIGN_SACCADE_SPAN;
            if (_head_angle >= 90)
              _head_angle_span = -ALIGN_SACCADE_SPAN;
            _head_angle += _head_angle_span;
            turnHead(_head_angle);
          }
        }
        else
          // The head did not reach the limit angle, the head must continues in the same direction
          turnHead(_head_angle += _head_angle_span);
      }
      else
      // The current echo is farther or equal to the previous, the head must reverse direction
      {
        _head_angle_span = - _head_angle_span;
        _head_angle += _head_angle_span;
        turnHead(_head_angle);
        // if ((_penultimate_ultrasonic_measure >= _previous_ultrasonic_measure) &&  ((_echo_alignment_step > 2) || (_penultimate_ultrasonic_measure == NO_ECHO_DISTANCE)))
        if ((_penultimate_ultrasonic_measure >= _previous_ultrasonic_measure) &&  (_echo_alignment_step > 2))
        // The head passed the minimum echo distance after two measures in the same direction: the minimum is at the previous angle
        // TODO make sure the two measures are in the same direction
        {
          _min_ultrasonic_measure = _previous_ultrasonic_measure;
          Serial.println("Aligned at angle: " + String(_head_angle) + ", measure " + String(_min_ultrasonic_measure));
          _is_enacting_head_alignment = false;
          _next_saccade_time = millis() + ECHO_MONITOR_PERIOD; // Wait before monitoring again
        }
      }
    }
    else
    // Watch for variation in ultrasonic measure to trigger alignment
    {
      _next_saccade_time = millis() + ECHO_MONITOR_PERIOD;
      _current_ultrasonic_measure = measureUltrasonicEcho();
      // Check the variation from the least aligned measure
      if (abs(_current_ultrasonic_measure - _min_ultrasonic_measure) > ECHO_MONITOR_VARIATION)
      {
        Serial.print("Trigger alignment from Angle: " +String(_head_angle) + ", measure: " + String(_current_ultrasonic_measure));
        Serial.println(", variation: " + String(_current_ultrasonic_measure - _min_ultrasonic_measure));
        beginEchoAlignment();
      }
    }
    // Check the variation from the last 50ms
    if (abs(_current_ultrasonic_measure - _previous_ultrasonic_measure) > ECHO_MONITOR_VARIATION &&
        abs(_current_ultrasonic_measure - _previous_ultrasonic_measure) < 9000 )
      _lost_focus = true;
    _penultimate_ultrasonic_measure = _previous_ultrasonic_measure;
    _previous_ultrasonic_measure = _current_ultrasonic_measure;
  }
}

// Return the last ultrasonic measure
int Head::get_ultrasonic_measure()
{
  return _current_ultrasonic_measure;
}

void Head::outcome(JSONVar & outcome_object)
{
  outcome_object["head_angle"] = _head_angle;

  // The latest measure obtained from echo alignment
  outcome_object["echo_distance"] = _min_ultrasonic_measure;
}

void Head::turnHead(int head_angle)
{
  _head_angle = constrain(head_angle, -90, 90);
  Serial.println("Turning head to: " + String(head_angle));
  _head.write(_head_angle + 90);
}

int Head::measureUltrasonicEcho()
{
  long echo_distance;
  digitalWrite(Trig_PIN,LOW);
  delayMicroseconds(5);
  digitalWrite(Trig_PIN,HIGH);
  delayMicroseconds(15);
  digitalWrite(Trig_PIN,LOW);
  echo_distance = pulseIn(Echo_PIN,HIGH, 10000);  // Timeout 10 milliseconds, otherwise it blocks the main loop!
  echo_distance = (int)(echo_distance * 0.1657);  // Convert to mm
  if (echo_distance == 0) echo_distance = 10000;  // Zero counts for far away
  //Serial.println("Angle " +String(_head_angle) + " measure " + String(echo_distance));
  return echo_distance;
}

// Return the head direction toward the (x,y) point
int Head::head_direction(int x, int y)
{
  if (x < ROBOT_HEAD_X)
  {
    // The focus is behind the head
    if (y > 0)
      return 90;
    else
      return -90;
  }
  else
    // The focus is before the head
    return (int)(atan2(y, x-ROBOT_HEAD_X) * 180.0 / M_PI);
}
