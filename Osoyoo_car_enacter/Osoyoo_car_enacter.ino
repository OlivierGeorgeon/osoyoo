/*  ___   ___  ___  _   _  ___   ___   ____ ___  ____  
 * / _ \ /___)/ _ \| | | |/ _ \ / _ \ / ___) _ \|    \ 
 *| |_| |___ | |_| | |_| | |_| | |_| ( (__| |_| | | | |
 * \___/(___/ \___/ \__  |\___/ \___(_)____)___/|_|_|_|
 *                  (____/ 
 * Arduino Mecanum Omni Direction Wheel Robot Car Lesson5 Wifi Control
 * Tutorial URL http://osoyoo.com/?p=30022
 * CopyRight www.osoyoo.com
 * 
 */
#include "omny_wheel_motion.h"
#include "calcDist.h"
#include "tracking.h"

#include "Servo_Scan.h"
#define pc "1"
#include "gyro.h"
#include "DelayAction.h"
DelayAction da;
#include "JsonOutcome.h"
JsonOutcome outcome;

#include "WifiBot.h"
WifiBot wifiBot = WifiBot("osoyoo_robot", 8888);

#include "WiFiEsp.h"
#include "WiFiEspUDP.h"

// use a ring buffer to increase speed and reduce memory allocation
char packetBuffer[5];

unsigned long endTime = 0;
int actionStep = 0;
float somme_gyroZ = 0;

void setup()
{
// init_GPIO();
  Serial.begin(9600);   // initialize serial for debugging
  servo_port();
  set();
  if (pc == "1"){
    wifiBot.wifiInitLocal();
  }
  if (pc == "2"){
    wifiBot.wifiInitRouter();
  }

  mpu_setup();
  ///da.setDelayAction(5000, scan(0, 180, 9), millis());
}

void loop()
{
    da.checkDelayAction(millis());
  int packetSize = wifiBot.Udp.parsePacket();
  gyro_update();
  if (packetSize) { // if you get a client,
    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    int len = wifiBot.Udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0;
    }
      char c=packetBuffer[0];

      endTime = millis() + 2000;
      actionStep = 1;
      switch (c)    //serial control instructions
        {  
        case '$':outcome.addValue("distance", (String) dist());break;
        case '8':go_forward(SPEED);break;
        case '4':left_turn(SPEED);break;
        case '6':right_turn(SPEED);break;
        case '2':go_back(SPEED);break;
        case '5':stop_Stop();break;
        case '0':until_line(SPEED);break;
        case 'D':outcome.addValue("distance", (String) dist());break;
        case 'S': 
                  int angle_tete_robot = scan(0, 180, 9);
                  float distance_objet_proche = dist();

                  outcome.addValue("Angle", (String) angle_tete_robot);
                  outcome.addValue("distance", (String) distance_objet_proche);
                  
                  break;
        default:break;
      }

    }
    if ( tracking()) // la fonction renvoi true si elle capte une ligne noir
    {
      stop_Stop();
      go_back(SPEED);//recule
      actionStep = 1;
      endTime = millis() + 1000; //1sec
    }
    if ((endTime < millis()) && (actionStep == 1))
    {
      stop_Stop();

      //Send outcome to PC
      outcome.addValue( "gyroZ", (String) (gyroZ()));
      wifiBot.sendOutcome(outcome.get());
      outcome.clear();
      actionStep = 0;
    }
    if(actionStep == 0)
    {
        reset_gyroZ(); //calibrer l'angle Z à 0 tant qu'il n'a pas fait d'action
    }
    
}
