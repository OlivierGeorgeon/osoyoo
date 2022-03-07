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
#include "LightSensor.h"
LightSensor ls;


#define WifiMode "R"        //Définir le mode de wifi du robot, 'R' pour routeur et 'W' pour la connexion au robot

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
char action = ' ';

unsigned long endTime = 0;
int actionStep = 0;
float somme_gyroZ = 0;
int floorOutcome = 0;

void setup()
{
// init_GPIO();
//  head = Head();
  Serial.begin(9600);   // initialize serial for debugging
  
  head.servo_port();
  
  head.distUS.setup();
  if (WifiMode == "W"){

    wifiBot.wifiInitLocal();
  }
  if (WifiMode == "R"){
    wifiBot.wifiInitRouter();
  }

  // mpu_setup();
  // compass_setup();

  //Exemple: da.setDelayAction(2000, [](){Serial.println("ok tout les 2s");}, millis());
  //da.setDelayAction(5000, distances_loop(angle_tete_robot, distance_objet_proche), millis());
}

void loop()
{
  da.checkDelayAction(millis());
  
  int packetSize = wifiBot.Udp.parsePacket();
  // gyro_update();

  if (packetSize) { // if you get a client,
    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    int len = wifiBot.Udp.read(packetBuffer, 255);

    if (len > 0) {
      packetBuffer[len] = 0;
    }

    JSONVar jsonReceive = JSON.parse(packetBuffer);
    if (jsonReceive.hasOwnProperty("action")) {
      action = ((const char*) jsonReceive["action"])[0];
    }

    Serial.print(action);

    endTime = millis() + 2000;
    actionStep = 1;

    switch (action)    //serial control instructions
    {  
      case '8':go_forward(SPEED);break;
      case '4':left_turn(SPEED);break;
      case '6':right_turn(SPEED);break;
      case '2':go_back(SPEED);break;
      case '5':stop_Stop();break;
      case '0':ls.until_line(SPEED);break;
      case 'D':outcome.addValue("echo_distance", (String) head.distUS.dist());break;
      case 'S': head.scan(0, 180, 9, 0);break;               
      default:break;
    }
  }
  
  if (ls.tracking() > 0) // la fonction renvoi true si elle capte une ligne noir
  {
    stop_Stop();
    floorOutcome = ls.tracking();
    go_back(SPEED);//recule
    actionStep = 1;
    endTime = millis() + 1000; //1sec
  }
  
  if ((endTime < millis()) && (actionStep == 1))
  {
    stop_Stop();
    
    //Send outcome to PC
    // renvoi JSON du degres de mouvement
    outcome.addValue("echo_distance", (String) head.distUS.dist());
    outcome.addValue("head_angle", (String) (head.angle_actuelle -  90)); 
    // outcome.addValue( "yaw", (String) (gyroZ()));
    outcome.addValue( "floor", (String) floorOutcome);
    outcome.addValue( "status", (String) floorOutcome);
    //renvoi JSON du azimut
    // outcome.addValue( "compass", (String) (degreesNorth()));
    wifiBot.sendOutcome(outcome.get());
    outcome.clear();
    actionStep = 0;
    floorOutcome = 0;
  }
  if(actionStep == 0)
  {
      // reset_gyroZ(); //calibrer l'angle Z à 0 tant qu'il n'a pas fait d'action
  }
}
