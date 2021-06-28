/*
  Imu_control.cpp - library for controlling the GY521 / MPU6050 IMU
  Created by Olivier Georgeon, june 28 2021
  released into the public domain
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

  // Set threshold sensivty. Default 3.
  // If you don't want use threshold, comment this line or set 0.
  _mpu.setThreshold(3);

}
Imu_control::begin()
{
  _yaw = 0;
}
Imu_control::update()
{
  unsigned long timer = millis();
  if (_next_imu_read_time < timer)
  {
    _next_imu_read_time = timer + IMU_READ_PERIOD;

    // Read normalized values
    Vector norm = _mpu.readNormalizeGyro();

    // Calculate Pitch, Roll and Yaw
    _yaw = _yaw + norm.ZAxis * IMU_READ_PERIOD / 1000;

    // Output raw
    Serial.print("Yaw = ");
    Serial.println(_yaw);
  }
}
Imu_control::end()
{
}
