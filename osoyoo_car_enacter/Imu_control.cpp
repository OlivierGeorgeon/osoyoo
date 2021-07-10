/*
  Imu_control.cpp - library for controlling the GY521 / MPU6050 IMU
  Created by Olivier Georgeon, june 28 2021
  Uses Korneliusz Jarzebski's MPU6050 library provided in the ELEGOO kit
  released into the public domain

  Attention: You must reset the arduino after turning the power on otherwise the IMU is not properly calibrate
*/
#include "Arduino.h"
#include "Imu_control.h"
#include <Wire.h>
#include <MPU6050.h>

Imu_control::Imu_control()
{
  _next_imu_read_time = 0;
  _yaw = 0;
}
Imu_control::setup()
{
  //Serial.begin(9200);

  // Initialize MPU6050
  while(!_mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_2G))
  {
    Serial.println("Could not find a valid MPU6050 sensor, check wiring!");
    Serial.println("You may need to comment line 54 in library MPU6050.cpp");
    delay(500);
  }

  // Calibrate gyroscope. The calibration must be at rest.
  // If you don't want calibrate, comment this line.
  _mpu.calibrateGyro();
  Serial.println("Gyroscope calibrated");

  // Set threshold sensitivity. Default 3.
  // If you don't want use threshold, comment this line or set 0.
  _mpu.setThreshold(3); // Tried without but gives absurd results

  // Set DLP Filter
  // See https://ulrichbuschbaum.wordpress.com/2015/01/18/using-the-mpu6050s-dlpf/
  _mpu.setDLPFMode(4);  // Filter out frequencies over 21 Hz


}
Imu_control::begin()
{
  _yaw = 0;
  _max_acceleration = 0;
  _min_acceleration = 0;
  _max_speed = 0;
  _xSpeed = 0;
  _xDistance = 0;
}
Imu_control::update()
{
  unsigned long timer = millis();
  if (_next_imu_read_time < timer)
  {
    _next_imu_read_time = timer + IMU_READ_PERIOD;

    // Read normalized values
    Vector normAccel = _mpu.readNormalizeAccel();
    Vector normGyro = _mpu.readNormalizeGyro();

    // Integrate Yaw during the interaction
    _yaw = _yaw + normGyro.ZAxis * IMU_READ_PERIOD / 1000;

    if (normAccel.XAxis > _max_acceleration) _max_acceleration =  normAccel.XAxis;
    if (normAccel.XAxis < _min_acceleration) _min_acceleration =  normAccel.XAxis;

    _xSpeed += (normAccel.XAxis) * IMU_READ_PERIOD / 1000;

    if (abs(_xSpeed) > _max_speed) _max_speed = abs(_xSpeed);

    //Serial.println(normAccel.XAxis);
    //Serial.println(normAccel.ZAxis);
    //Serial.println(_xSpeed);
    _xDistance += _xSpeed * IMU_READ_PERIOD / 1000;

    // Output raw
    //Serial.print("Yaw = ");
    //Serial.println(_yaw);
  }
}
void Imu_control::outcome(JSONVar & outcome_object)
{
  outcome_object["yaw"] = _yaw;
  //outcome_object["max_acceleration"] = _max_acceleration;
  //outcome_object["min_acceleration"] = _min_acceleration;
  //outcome_object["max_speed"] = _max_speed;

  //Serial.println("End yaw = " + String(_yaw));
  //Serial.println("End distance " + String(_xDistance));
  //return _yaw;
}
