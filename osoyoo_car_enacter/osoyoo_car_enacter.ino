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
#include "Robot_define.h"
#include "Floor_change_retreat.h"
#include "Head_echo_alignment.h"
#include "Imu_control.h"
#include <WiFiEsp.h>
#include <WiFiEspUDP.h>
#include <Arduino_JSON.h>

#define SPEED 100
#define TURN_SPEED 90  
#define SHIFT_SPEED 130

#define TURN_TIME 500  
#define MOVE_TIME 500  

#define TURN_FRONT_ENDING_DELAY 100
#define TURN_FRONT_ENDING_ANGLE 3

#define ACTION_TURN_IN_SPOT_LEFT '1'
#define ACTION_GO_BACK '2'
#define ACTION_TURN_IN_SPOT_RIGHT '3'
#define ACTION_SHIFT_LEFT '4'
#define ACTION_STOP '5'
#define ACTION_SHIFT_RIGHT '6'
#define ACTION_TURN_LEFT '7'
#define ACTION_GO_ADVANCE '8'
#define ACTION_TURN_RIGHT '9'
#define ACTION_ALIGN_ROBOT '/'
#define ACTION_ALIGN_HEAD '*'
#define ACTION_ECHO_SCAN '-'

Omny_wheel_motion OWM;
Floor_change_retreat FCR(OWM);
Head_echo_alignment HEA;
Imu_control IMU;

int status = WL_IDLE_STATUS;
char packetBuffer[50];
WiFiEspUDP Udp;
unsigned int localPort = 8888;  // local port to listen on

void setup()
{
  OWM.setup();
  HEA.setup();
  Serial.begin(9600);   // initialize serial for debugging
  Serial.println("Serial initialized");

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

  Udp.begin(localPort);

  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Listening on port: ");
  Serial.println(localPort);
}

unsigned long action_start_time = 0;
unsigned long action_end_time = 0;
int interaction_step = 0;
bool is_enacting_action = false;
char action =' ';
String outcome = "0";
int robot_destination_angle = 0;

void loop()
{
  // Behavior floor change retreat
  FCR.update();

  // Behavior head echo alignment
  HEA.update();

  // IMU reading
  IMU.update();

  // If no interaction being enacted
  if (interaction_step == 0 )
  {
    // Watch the wifi for new action
    int packetSize = Udp.parsePacket();
    // If the received packet exceeds the size of packetBuffer defined above, Arduino will crash
    if (packetSize) {
      int len = Udp.read(packetBuffer, 255);
      //if (len > 0) {
        packetBuffer[len] = 0;
        Serial.print("Received action ");
        if (len == 1) {
          // Single character is the action
          action = packetBuffer[0];
          Serial.print(action);
        } else {
          // Multiple characters is json
          // https://github.com/arduino-libraries/Arduino_JSON/blob/master/examples/JSONObject/JSONObject.ino
          JSONVar myObject = JSON.parse(packetBuffer);
          Serial.print(myObject);
          if (myObject.hasOwnProperty("action")) {
            action = ((const char*) myObject["action"])[0];
          }
          if (myObject.hasOwnProperty("angle")) {
            robot_destination_angle = ((int) myObject["angle"]);
          }
        }
      //}
      Serial.print(" from ");
      IPAddress remoteIp = Udp.remoteIP();
      Serial.print(remoteIp);
      Serial.print("/");
      Serial.println(Udp.remotePort());

      action_start_time = millis();
      action_end_time = action_start_time + 1000;
      is_enacting_action = true;
      interaction_step = 1;
      IMU.begin();
      FCR._floor_outcome = 0; // Ignore floor change before the interaction
      outcome = "0";
      switch (action)
      {
        case ACTION_TURN_IN_SPOT_LEFT:
          action_end_time = millis() + TURN_SPOT_MAX_DURATION;
          robot_destination_angle = 45;
          HEA.turnHead(robot_destination_angle);  // Look at destination
          OWM.turnInSpotLeft(TURN_SPEED);
          break;
        case ACTION_GO_BACK:
          OWM.goBack(SPEED);
          break;
        case ACTION_TURN_IN_SPOT_RIGHT:
          action_end_time = millis() + TURN_SPOT_MAX_DURATION;
          robot_destination_angle = -45;
          HEA.turnHead(robot_destination_angle);
          OWM.turnInSpotRight(TURN_SPEED);
          break;
        case ACTION_SHIFT_LEFT:
          OWM.shiftLeft(SHIFT_SPEED);
          //action_end_time = millis() + 5000;
          break;
        case ACTION_STOP:
          OWM.stopMotion();
          break;
        case ACTION_SHIFT_RIGHT:
          //action_end_time = millis() + 5000;
          OWM.shiftRight(SHIFT_SPEED);
          break;
        case ACTION_TURN_LEFT:
          action_end_time = millis() + 250;
          OWM.turnLeft(SPEED);
          break;
        case ACTION_GO_ADVANCE:
          OWM.goForward(SPEED);
          break;
        case ACTION_TURN_RIGHT:
          action_end_time = millis() + 250;
          OWM.turnRight(SPEED);
          break;
        case ACTION_ALIGN_HEAD:
          HEA.beginEchoAlignment();
          action_end_time = millis() + 2000;
          break;
        case ACTION_ECHO_SCAN:
          HEA.beginEchoScan();
          action_end_time = millis() + 5000;
          break;
        case ACTION_ALIGN_ROBOT:
          action_end_time = millis() + 5000;
          //robot_destination_angle = HEA._head_angle;
          //Serial.println("Begin align robot angle : " + String(robot_destination_angle));
          HEA.turnHead(robot_destination_angle);  // Look at destination
          if ( robot_destination_angle < - TURN_FRONT_ENDING_ANGLE){
            OWM.turnInSpotRight(TURN_SPEED);
            //OWM.turnFrontRight(SPEED);
          }
          if ( robot_destination_angle > TURN_FRONT_ENDING_ANGLE){
            OWM.turnInSpotLeft(TURN_SPEED);
            //OWM.turnFrontLeft(SPEED);
          }
          break;
        default:
          break;
      }
    }
  }

  // If an interaction is being enacted
  if (interaction_step == 1)
  {
    switch (action)
    {
      case ACTION_GO_ADVANCE:
      case ACTION_TURN_RIGHT:
      case ACTION_TURN_LEFT:
        if (FCR._is_enacting) {
          FCR.extraDuration(RETREAT_EXTRA_DURATION); // Extend retreat duration because need to reverse speed
          outcome ="1";
          action_end_time = 0;
          interaction_step = 2;
        }
        else if (action_end_time < millis()) {
          interaction_step = 3;
        }
        break;
      case ACTION_TURN_IN_SPOT_LEFT:
        // Keep head aligned with destination angle
        HEA.turnHead(robot_destination_angle - IMU._yaw);
         // Stop before reaching 45°
        if (IMU._yaw > robot_destination_angle - TURN_SPOT_ENDING_ANGLE)
        {
          OWM.stopMotion();
          interaction_step = 2;
          action_end_time = millis() + TURN_SPOT_ENDING_DELAY;
        }
        // Stop at action end time
        else if (action_end_time < millis()) {
          interaction_step = 2;
        }
        break;
     case ACTION_TURN_IN_SPOT_RIGHT:
        // Keep head aligned with destination angle
        HEA.turnHead(robot_destination_angle - IMU._yaw);
        // Stop before reaching -45°
        if (IMU._yaw < robot_destination_angle + TURN_SPOT_ENDING_ANGLE)
        {
          OWM.stopMotion();
          interaction_step = 2;
          action_end_time = millis() + TURN_SPOT_ENDING_DELAY;
        }
        // Stop at action end time
        else if (action_end_time < millis()) {
          interaction_step = 2;
        }
        break;
      case ACTION_ALIGN_ROBOT:
        HEA.turnHead(robot_destination_angle - IMU._yaw); // Keep looking at destination
        if (((robot_destination_angle > TURN_FRONT_ENDING_ANGLE) && (IMU._yaw > robot_destination_angle - TURN_FRONT_ENDING_ANGLE)) ||
        ((robot_destination_angle < -TURN_FRONT_ENDING_ANGLE) && (IMU._yaw < robot_destination_angle + TURN_FRONT_ENDING_ANGLE)) ||
        (abs(robot_destination_angle) < TURN_FRONT_ENDING_ANGLE))
        {
          OWM.stopMotion();
          interaction_step = 2;
          action_end_time = millis() + TURN_FRONT_ENDING_DELAY;// give it time to immobilize before terminating interaction
        }
        break;
      case ACTION_ALIGN_HEAD:
      case ACTION_ECHO_SCAN:
        if (!HEA._is_enacting_head_alignment && !HEA._is_enacting_echo_scan)
        {
          action_end_time = 0;
          interaction_step = 3;
        }
        break;
      default:
        interaction_step = 2;
        break;
    }
  }

  // If an interaction is being terminated
  if (interaction_step == 2)
  {
    switch (action)
    {
      case ACTION_GO_ADVANCE:
      case ACTION_TURN_RIGHT:
      case ACTION_TURN_LEFT:
        if (!FCR._is_enacting) {
          interaction_step = 3;
        }
        break;
      case ACTION_TURN_IN_SPOT_LEFT:
      case ACTION_TURN_IN_SPOT_RIGHT:
        if (!FCR._is_enacting && action_end_time < millis() && !HEA._is_enacting_head_alignment) {
          Serial.println("interaction step = 3");
          interaction_step = 3;
        }
        break;
      default:
        if (action_end_time < millis()) {
          interaction_step = 3;
        }
        break;
    }
  }

  // End of interaction
  if ((interaction_step == 3))
  {
    JSONVar outcome_object;
    outcome_object["status"] = outcome;
    FCR.outcome(outcome_object);
    HEA.outcome(outcome_object);

    switch (action)
    {
      //case ACTION_GO_ADVANCE:
      case ACTION_ALIGN_HEAD:
      case ACTION_ECHO_SCAN:
        // HEA.outcome(outcome_object);
        break;
      default:
        OWM.stopMotion();
        break;
    }
    is_enacting_action = false;
    outcome_object["duration"] = millis() - action_start_time;

    interaction_step = 0;

    IMU.outcome(outcome_object);
    String outcome_json_string = JSON.stringify(outcome_object);
    Serial.println("Outcome string " + outcome_json_string);

    // Send the outcome to the IP address and port that sent the action
    Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    Udp.print(outcome_json_string);
    Udp.endPacket();
  }
}
