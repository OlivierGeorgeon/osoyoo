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
#include "Head_Dist.h"
Head_Dist HD;
#include "tracking.h"


#define WifiMode "R"        //Définir le mode de wifi du robot, 'R' pour routeur et 'W' pour la connexion au robot
#include "Servo_Scan.h"

#include "gyro.h"
#include "compass.h"

#include "JsonOutcome.h"
JsonOutcome outcome;

#include "Head.h";
Head head;

#include "DelayAction.h"
DelayAction da;

#include "WifiBot.h"
WifiBot wifiBot = WifiBot("osoyoo_robot2", 8888);

#include "WiFiEsp.h"
#include "WiFiEspUDP.h"

#include "Arduino_JSON.h"

// use a ring buffer to increase speed and reduce memory allocation
char packetBuffer[100];

unsigned long endTime = 0;
int actionStep = 0;
float somme_gyroZ = 0;
int angle_tete_robot = 90;
float distance_objet_proche = 0;

void setup()
{
// init_GPIO();
  head = Head();
  Serial.begin(9600);   // initialize serial for debugging
  
  head.servo_port();
  
  HD.setup();
  if (WifiMode == "W"){

    wifiBot.wifiInitLocal();
  }
  if (WifiMode == "R"){
    wifiBot.wifiInitRouter();
  }

  mpu_setup();
  compass_setup();

  //Exemple: da.setDelayAction(2000, [](){Serial.println("ok tout les 2s");}, millis());
  //da.setDelayAction(5000, distances_loop(angle_tete_robot, distance_objet_proche), millis());
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

    JSONVar jsonReceive = JSON.parse(packetBuffer);
    Serial.println(JSON.stringify(jsonReceive));
    String strAction = JSON.stringify(jsonReceive["action"]);

    int str_len = strAction.length() + 1;
    char action[str_len];
    strAction.toCharArray(action, str_len);

    endTime = millis() + 2000;
    actionStep = 1;

    switch (action[1])    //serial control instructions
    {  
      case '$':outcome.addValue("distance", (String) HD.dist());break;
      case '8':go_forward(SPEED);break;
      case '4':left_turn(SPEED);break;
      case '6':right_turn(SPEED);break;
      case '2':go_back(SPEED);break;
      case '5':stop_Stop();break;
      case '0':until_line(SPEED);break;
      case 'B':
               distances_loop(angle_tete_robot, distance_objet_proche);
               outcome.addValue("head_angle", (String) angle_tete_robot);
               outcome.addValue("echo_distance", (String) distance_objet_proche);
      case 'D':outcome.addValue("distance", (String) HD.dist());break;
      case 'T':
                  angle_tete_robot = scan(0, 180, 9, 0);
                  distance_objet_proche = HD.dist();
                  outcome.addValue("head_angle", (String) angle_tete_robot);
                  outcome.addValue("echo_distance", (String) distance_objet_proche);  
                  break;
       case 'S': head.scan(0, 180, 9, 0);break;
        default:break;
      }
  }
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
      // renvoi JSON du degres de mouvement
      outcome.addValue( "gyroZ", (String) (gyroZ()));
      //renvoi JSON du azimut
      outcome.addValue( "compass", (String) (degreesNorth()));
      wifiBot.sendOutcome(outcome.get());
      outcome.clear();
      actionStep = 0;
    }
    if(actionStep == 0)
    {
        reset_gyroZ(); //calibrer l'angle Z à 0 tant qu'il n'a pas fait d'action
    }
}
