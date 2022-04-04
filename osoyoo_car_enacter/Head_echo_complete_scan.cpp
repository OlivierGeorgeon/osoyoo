/*
  Head_echo_complete_scan.h - library for Osoyoo car align head towards closest ultrasonic echo.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
#include "Arduino.h"
#include "Robot_define.h"
#include "Head_echo_complete_scan.h"
#include <Servo.h>
//#define SERVO_PIN   13  //servo connect to D5
#define Echo_PIN    31  // Ultrasonic Echo pin connect to A5
#define Trig_PIN    30  // Ultrasonic Trig pin connect to A4



Head_echo_complete_scan::Head_echo_complete_scan()
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
  _sign_array = significant_array();
  _current_index = 0;
}

void Head_echo_complete_scan::setup()
{
  // init HC-SR04 ultrasonic Echo sensor
  pinMode(Trig_PIN, OUTPUT);
  pinMode(Echo_PIN,INPUT);
  digitalWrite(Trig_PIN,LOW);
  // init servo
  _head.attach(ROBOT_SERVO_PIN);
  turnHead(0); // Head straight ahead
  //Serial.println("HEA initialized");
}

void Head_echo_complete_scan::beginEchoAlignment()
{
  _is_enacting_head_alignment = true;
  _penultimate_ultrasonic_measure = 1;  // Reinitialize previous measures so it will not ...
  _previous_ultrasonic_measure = 10001; // ... believe that the next measure is a minimum
  _head_angle_span = SACCADE_SPAN;
  _echo_alignment_step = 0;
  //turnHead(_head_angle - _head_angle_span);
  _next_saccade_time = millis() + SACCADE_DURATION;
}
void Head_echo_complete_scan::beginEchoScan()
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

void Head_echo_complete_scan::update()
{
  if (millis() > _next_saccade_time )
  {
    if (_is_enacting_head_alignment)
    {
      _echo_alignment_step++;
      _next_saccade_time = millis() + SACCADE_DURATION;
      int current_ultrasonic_measure = measureUltrasonicEcho();
      _sign_array.distances[_current_index] = current_ultrasonic_measure;
      _sign_array.angles[_current_index] = _head_angle;
      _current_index++;
      Serial.println("Step: " + String(_echo_alignment_step) + ", Angle: " +String(_head_angle) + ", measure: " + String(current_ultrasonic_measure));
      if (_previous_ultrasonic_measure > current_ultrasonic_measure )
      // The echo is closer
      {
        if ((_head_angle <= -90) || (_head_angle >= 90))
        // The head reached the limit angle
        {
          if (_echo_alignment_step > 1)
          // The echo is closer after several steps then the min distance is here
          {
            _min_ultrasonic_measure = current_ultrasonic_measure;
            Serial.println("Step: " + String(_echo_alignment_step) + ", Aligned at edge angle " + String(_head_angle) + " measure " + String(_min_ultrasonic_measure));
            _is_enacting_head_alignment = false;
            _next_saccade_time = millis() + ECHO_MONITOR_PERIOD; // Wait before monitoring again
          } else
          // The echo is closer on the first step then we need to reverse head movement
          {
            _head_angle_span = - _head_angle_span;
            _head_angle += _head_angle_span;
            turnHead(_head_angle);
          }
        } else
        // The head did not reach the limit angle, the head must continues in the same direction
        {
          turnHead(_head_angle += _head_angle_span);
        }
      } else
      // The echo is farther, the head must turn in the other direction
      {
        _head_angle_span = - _head_angle_span;
        _head_angle += _head_angle_span;
        turnHead(_head_angle);
        if ((_penultimate_ultrasonic_measure >= _previous_ultrasonic_measure) &&  (_echo_alignment_step > 2))
        // The head passed the minimum echo distance after two measure: the minimum is here
        {
          _min_ultrasonic_measure = _previous_ultrasonic_measure;
          Serial.println("Step: " + String(_echo_alignment_step) + ", Aligned at angle " + String(_head_angle) + " measure " + String(_min_ultrasonic_measure));
          _is_enacting_head_alignment = false;
          _next_saccade_time = millis() + ECHO_MONITOR_PERIOD; // Wait before monitoring again
        }
      }
      _penultimate_ultrasonic_measure = _previous_ultrasonic_measure;
      _previous_ultrasonic_measure = current_ultrasonic_measure;
    }
    else if (_is_enacting_echo_scan)
    {
      int current_ultrasonic_measure = measureUltrasonicEcho();
      _next_saccade_time = millis() + SACCADE_DURATION;
      if (current_ultrasonic_measure < _min_ultrasonic_measure){
        _min_ultrasonic_measure = current_ultrasonic_measure;
        _angle_min_ultrasonic_measure = _head_angle;
      }
      _head_angle += _head_angle_span;
      if (abs(_head_angle) > 90){ // The scan is over, move to the angle of the min measure
        _is_enacting_echo_scan = false;
        _head_angle  = _angle_min_ultrasonic_measure;
        // turnHead(_angle_min_ultrasonic_measure);
        Serial.println("Scan aligned at angle: " + String(_head_angle) + ", measure: " + String(_min_ultrasonic_measure));
        _next_saccade_time = millis() + ECHO_MONITOR_PERIOD; // Wait before monitoring again
      }
      turnHead(_head_angle);
    }
    else // Watch for variation in ultrasonic measure to trigger alignment
    {
      _next_saccade_time = millis() + ECHO_MONITOR_PERIOD;
      int current_ultrasonic_measure = measureUltrasonicEcho();

      if (abs(current_ultrasonic_measure - _min_ultrasonic_measure) > ECHO_MONITOR_VARIATION)
      {
        Serial.print("Angle: " +String(_head_angle) + ", measure: " + String(current_ultrasonic_measure));
        Serial.println(", Trigger variation: " + String(current_ultrasonic_measure - _min_ultrasonic_measure));
        beginEchoAlignment();
      }
    }
  }
}

void Head_echo_complete_scan::outcome(JSONVar & outcome_object)
{
    // For every index i in _sign_array, set _sign_array.sign[i] to true if _sign_array.distances[i] < _sign_array.distances[i-1] and _sign_array.distances[i] < _sign_array.distances[i+1] 
    // and false otherwise
    for (int i = 0; i < _sign_array.size; i++)
    {
      if (_sign_array.distances[i] < _sign_array.distances[i+1])
      {
        if(i != 0 and _sign_array.distances[i] > _sign_array.distances[i-1]){
            continue;
        }
        _sign_array.sign[i] = true;
      }
      else
      {
        _sign_array.sign[i] = false;
      }
    }

    // TODO: HELP: Write every _sign_array.distances[i] in the
    // outcome_object if _sign_array.sign[i] is true
    int nb_echo = 0;
    for (int i = 0; i < _sign_array.size; i++){
        if (_sign_array.sign[i]){
            outcome_object["head_angle_"+ std::to_string(nb_echo)] = _sign_array.angles[i];
            outcome_object["echo_distance_"+ std::to_string(nb_echo)] = _sign_array.distances[i];
        }
    }
    
    /*
  outcome_object["head_angle"] = _head_angle;

  // The latest measure obtained from echo alignment
  outcome_object["echo_distance"] = _min_ultrasonic_measure;
    */
  // Make a new measure
  // outcome_object["echo_distance"] = measureUltrasonicEcho(); Not working
}

void Head_echo_complete_scan::turnHead(int head_angle)
{
  _head_angle = constrain(head_angle, -90, 90);
  _head.write(_head_angle + 90);
}

int Head_echo_complete_scan::measureUltrasonicEcho()
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