#include <Arduino.h>
#include "tracking.h"
#include "omny_wheel_motion.h"

bool tracking()
{
  String senstr="";
  // quand un capteur affiche 0 ca veut dire quil capte la ligne noire
  int s0 = digitalRead(sensor0);
  int s1 = digitalRead(sensor1);
  int s2 = digitalRead(sensor2);
  int s3 = digitalRead(sensor3);
  int s4 = digitalRead(sensor4);


  int sensorvalue=32;
  sensorvalue +=s0*16+s1*8+s2*4+s3*2+s4;//operation pour pouvoir convertrir en code binair
  senstr= String(sensorvalue,BIN);//fonction qui transform en code binair
  senstr=senstr.substring(1,6);
  return senstr!="11111";//si au moins un des capteurs capte du noir alors :
}