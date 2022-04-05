#include <Arduino.h>
#include "LightSensor.h"
#include "../wheel/omny_wheel_motion.h"

LightSensor::LightSensor(){}


int LightSensor::tracking() {
  // return 1 if line
  int s0 = !digitalRead(sensor0); // Right sensor
  int s1 = !digitalRead(sensor1);
  int s2 = !digitalRead(sensor2);
  int s3 = !digitalRead(sensor3);
  int s4 = !digitalRead(sensor4); // Left sensor

  int sensorInt = s0*16+s1*8+s2*4+s3*2+s4;

  switch(sensorInt) {
    case 0b10000:
    case 0b11000:
    case 0b01000:
      return 1; //01
    case 0b11111:
    case 0b11011:
    case 0b01110:
    case 0b01010:
    case 0b00100:
      return 3; //11
    case 0b00001:
    case 0b00011:
    case 0b00010:
      return 2; //10
    default:
      return 0;
  }
}

void LightSensor::until_line(int speed) {
    while (tracking() <= 0) {
        go_forward(speed);
    }
    stop_Stop();
}