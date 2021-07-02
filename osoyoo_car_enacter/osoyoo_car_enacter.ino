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
#include "arduino_secrets.h"
#include "Floor_change_retreat.h"
#include "Head_echo_alignment.h"
#include "Imu_control.h"
#include <WiFiEsp.h>
#include <WiFiEspUDP.h>

#define SPEED 85    
#define TURN_SPEED 90  
#define SHIFT_SPEED 130  

#define TURN_TIME 500  
#define MOVE_TIME 500  

#define ENDING_DELAY 250
#define ENDING_ANGLE 11


Omny_wheel_motion OWM;
Floor_change_retreat FCR(OWM);
Head_echo_alignment HEA;
Imu_control IMU;

int status = WL_IDLE_STATUS;
// use a ring buffer to increase speed and reduce memory allocation
char packetBuffer[5];
WiFiEspUDP Udp;
unsigned int localPort = 8888;  // local port to listen on

void setup()
{
  OWM.setup();
  HEA.setup();
  Serial.begin(9600);   // initialize serial for debugging
  IMU.setup();

  Serial1.begin(115200);
  Serial1.write("AT+UART_DEF=9600,8,1,0,0\r\n");
  delay(200);
  Serial1.write("AT+RST\r\n");
  delay(200);
  Serial1.begin(9600);    // initialize serial for ESP module
  WiFi.init(&Serial1);    // initialize ESP module

  // check for the presence of the shield
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue
    while (true);
  }
  if (SECRET_WIFI_TYPE == "AP") { // Wifi parameters in arduino_secret.h
    // Connecting to wifi as an Access Point (AP)
    char ssid[] = "osoyoo_robot";
    Serial.print("Attempting to start AP ");
    Serial.println(ssid);
    status = WiFi.beginAP(ssid, 10, "", 0);
  } else {
    // Connecting to wifi as a Station (STA)
    char ssid[] = SECRET_SSID;
    char pass[] = SECRET_PASS;
    while (status != WL_CONNECTED) {
      Serial.print("Attempting to connect to WPA SSID: ");
      Serial.println(ssid);
      status = WiFi.begin(ssid, pass);
    }
  }

  Serial.println("Robot connected to the network");
  printWifiStatus();
  Udp.begin(localPort);
  
  Serial.print("Listening on port ");
  Serial.println(localPort);
}

bool is_enacting_floor_change_retreat = false;
bool is_enacting_head_alignment = false;
unsigned long action_end_time = 0;
bool is_enacting_action = false;
bool is_ending_interaction = false;
char action =' ';
String outcome = "0";
int robot_angle_alignment = 0;

void loop()
{
  // Behavior floor change retreat
  is_enacting_floor_change_retreat = FCR.update();
  if (is_enacting_floor_change_retreat && is_enacting_action && (action == 'A') ) {
    outcome ="1";
    action_end_time = 0;
  }

  // Behavior head echo alignment
  is_enacting_head_alignment = HEA.update();
  if (!is_enacting_action && !is_enacting_floor_change_retreat ) {
    HEA.monitor(); // Could be included in update()
  }
  if (is_enacting_action && (action == 'E') && !is_enacting_head_alignment) {
    outcome = HEA.outcome();
    action_end_time = 0;
  }

  // IMU reading
  IMU.update();

  if (is_enacting_action)
  {
    if (action_end_time < millis())
    {
      //char outcome = '0';
      switch (action)
      {
        case 'A':
          if (is_enacting_floor_change_retreat) {
            FCR.extraDuration(RETREAT_EXTRA_DURATION); // Extend retreat duration because need to reverse speed
          } else {
            OWM.stopMotion(); // Stop motion unless a reflex is being enacted
          }
          break;
        case 'B':
          OWM.stopMotion();
          break;
        case 'E':
          OWM.stopMotion();
          break;
        case 'C':
          OWM.stopMotion();
          break;
        case 'G':
          OWM.stopMotion();
          break;
        case 'Z':
          is_ending_interaction = false;
          OWM.stopMotion();
          break;
      }
      outcome += "Y" + String(IMU.end());
      is_enacting_action = false;
      // Send the outcome to the IP address and port that sent the action
      Serial.println("Outcome string " + outcome);

      //StaticJsonDocument<200> doc;

      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.print(outcome);
      //Udp.write(outcome_char);
      Udp.endPacket();
    }
    else // If action being enacted
    {
      if (action == 'C') {
        /*if (is_enacting_head_alignment) {
          stop_motion();
          action_end_time = 0;
        }*/
      }
      if (action == 'Z') {
         if (((robot_angle_alignment > ENDING_ANGLE) && (IMU._yaw > robot_angle_alignment - ENDING_ANGLE)) ||
         ((robot_angle_alignment < -ENDING_ANGLE) && (IMU._yaw < robot_angle_alignment + ENDING_ANGLE)) ||
         (abs(robot_angle_alignment) < ENDING_ANGLE)) {
           HEA.turnHead(90);  // Look ahead
           OWM.stopMotion();
           if (!is_ending_interaction){
             is_ending_interaction = true;
             action_end_time = millis() + ENDING_DELAY;// leave time to immobilize and then end interaction
           }
         }
      }
    }
  }
  else // If is not enacting action
  {
    // Watch the wifi for new action
    int packetSize = Udp.parsePacket();
    if (packetSize) {                               // if you get a client,
      int len = Udp.read(packetBuffer, 255);
      if (len > 0) {
        packetBuffer[len] = 0;
      }
      action = packetBuffer[0];
      Serial.print("Received action ");
      Serial.print(action);
      Serial.print(" from ");
      IPAddress remoteIp = Udp.remoteIP();
      Serial.print(remoteIp);
      Serial.print("/");
      Serial.println(Udp.remotePort());

      action_end_time = millis() + 1000;
      is_enacting_action = true;
      IMU.begin();
      outcome = "0";
      switch (action)    //serial control instructions
      {
        case 'A':
          OWM.goForward(SPEED);
          action_end_time = millis() + 1000;
          break;
        case 'B':
          OWM.goBack(SPEED);
          action_end_time = millis() + 1000;
          break;
        case 'S':
          OWM.stopMotion();break;
        case 'C': //turn in spot clockwise
          action_end_time = millis() + 1000;
          HEA.turnHead(90);  // Look ahead
          OWM.turnInSpotRight(TURN_SPEED);
          break;
        case 'G':
          action_end_time = millis() + 1000;
          HEA.turnHead(90);  // Look ahead
          OWM.turnInSpotLeft(TURN_SPEED);
          break;
        case 'E': // Align head
          HEA.begin();
          action_end_time = millis() + 10000;
          break;
        case 'Z': // Align robot body to head
          action_end_time = millis() + 5000;
          robot_angle_alignment = HEA._head_angle - 90;
          Serial.println("Begin align robot angle : " + String(robot_angle_alignment));
          if ( robot_angle_alignment < - ENDING_ANGLE){
            OWM.turnInSpotRight(SPEED);
          }
          if ( robot_angle_alignment > ENDING_ANGLE){
            OWM.turnInSpotLeft(SPEED);
          }
          break;
        default:
          break;
      }
    }
  }
}


void printWifiStatus()
{
  // print the SSID of the network you're attached to
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());
  // print your WiFi shield's IP address
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
}
