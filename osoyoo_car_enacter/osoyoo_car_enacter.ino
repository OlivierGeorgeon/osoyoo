/*  ___   ___  ___  _   _  ___   ___   ____ ___  ____  
 * / _ \ /___)/ _ \| | | |/ _ \ / _ \ / ___) _ \|    \ 
 *| |_| |___ | |_| | |_| | |_| | |_| ( (__| |_| | | | |
 * \___/(___/ \___/ \__  |\___/ \___(_)____)___/|_|_|_|
 *                  (____/ 
 * Inspired form Arduino Mecanum Omni Direction Wheel Robot Car Lesson5 Wifi Control
 * Tutorial URL http://osoyoo.com/?p=30022
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

// #include <SoftwareSerial.h> // AJOUT ERREUR. Commenté par Olivier je ne sais pas d'ou ca sort.

#define SPEED 100
#define TURN_SPEED 100
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
#define ACTION_SCAN_DIRECTION '+'

#define TURN_SPOT_ANGLE 60

Omny_wheel_motion OWM;
Floor_change_retreat FCR(OWM);
Head_echo_alignment HEA;
Imu_control IMU;

char packetBuffer[50];
WiFiEspUDP Udp;
unsigned int localPort = 8888;  // local port to listen on

void setup()
{
  // Initialize serial for debugging
  Serial.begin(9600);
  // Serial.println("Serial initialized");

  // Connect to the wifi board
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
  // Connect to the wifi network
  int status = WL_IDLE_STATUS;
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
      // Serial.print("Attempting to connect to WPA SSID: ");
      // Serial.println(ssid);
      status = WiFi.begin(ssid, pass);
    }
  }
  Udp.begin(localPort);

  // Serial.print("IP Address: ");
  // Serial.println(WiFi.localIP());
  // Serial.print("Listening on port: ");
  // Serial.println(localPort);

  // Initialize the automatic behaviors
  OWM.setup();
  HEA.setup();
  IMU.setup();
  // Setup the imu twice otherwise the calibration is wrong. I don't know why.
  // Probably something to do with the order in which the imu registers are written.
  delay(100);
  IMU.setup();
  delay(100);
  IMU.setup();

  // Serial.println("--- Robot initialized ---");

  // Initialize PIN 13 LED for debugging
  pinMode(LED_BUILTIN, OUTPUT);
  //digitalWrite(LED_BUILTIN, HIGH);
}

unsigned long action_start_time = 0;
unsigned long action_end_time = 0;
int interaction_step = 0;
char action =' ';
String status = "0"; // The outcome information used for sequential learning
int robot_destination_angle = 0;
unsigned long blink_end_time = 0;
bool blink_on = true;

void loop()
{
  // Display a flashing led to check whether something is freezing the main loop
  if (millis()> blink_end_time){
    if (blink_on) {
      digitalWrite(LED_BUILTIN, HIGH); // for debug
      blink_on = false;
    }else {
      digitalWrite(LED_BUILTIN, LOW); // for debug
      blink_on = true;
    }
    blink_end_time = millis() + 50;
  }

  // Behavior floor change retreat
  FCR.update();

  // Behavior head echo alignment
  HEA.update();

  // Behavior IMU
  //digitalWrite(LED_BUILTIN, LOW); // for debug
  int shock_event = IMU.update(interaction_step);
  // if (blink_on) {digitalWrite(LED_BUILTIN, HIGH);} // for debug

  // STEP 0: no interaction being enacted
  // Watching for message sent from PC
  if (interaction_step == 0 )
  {
    // Watch the wifi for new action
    int packetSize = Udp.parsePacket();
    // If the received packet exceeds the size of packetBuffer defined above, Arduino will crash
    if (packetSize) {
      int action_angle = 0;
      int len = Udp.read(packetBuffer, 512);
      packetBuffer[len] = 0;
      //Serial.print("Received action ");
      if (len == 1) {
        // Single character is the action
        action = packetBuffer[0];
        //Serial.print(action);
      } else {
        // Multiple characters is json
        // https://github.com/arduino-libraries/Arduino_JSON/blob/master/examples/JSONObject/JSONObject.ino
        JSONVar myObject = JSON.parse(packetBuffer);
        //Serial.print(myObject);
        if (myObject.hasOwnProperty("action")) {
          action = ((const char*) myObject["action"])[0];
        }
        if (myObject.hasOwnProperty("angle")) {
          action_angle = ((int) myObject["angle"]);
        }
      }
      //Serial.print(" from ");
      IPAddress remoteIp = Udp.remoteIP();
      //Serial.print(remoteIp);
      //Serial.print("/");
      //Serial.println(Udp.remotePort());

      action_start_time = millis();
      action_end_time = action_start_time + 1000;
      interaction_step = 1;
      IMU.begin();
      shock_event = 0; // reset event from previous interaction
      FCR._floor_outcome = 0; // Reset possible floor change when the robot was placed on the floor
      //digitalWrite(LED_BUILTIN, LOW); // for debug
      status = "0";
      switch (action)
      {
        case ACTION_TURN_IN_SPOT_LEFT:
          action_end_time = millis() + TURN_SPOT_MAX_DURATION;
          robot_destination_angle = TURN_SPOT_ANGLE;
          HEA.turnHead(robot_destination_angle);  // Look at destination
          OWM.turnInSpotLeft(TURN_SPEED);
          break;
        case ACTION_GO_BACK:
          OWM.goBack(SPEED);
          break;
        case ACTION_TURN_IN_SPOT_RIGHT:
          action_end_time = millis() + TURN_SPOT_MAX_DURATION;
          robot_destination_angle = -TURN_SPOT_ANGLE;
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
        case ACTION_SCAN_DIRECTION:
          HEA.turnHead(action_angle);
          HEA.beginEchoAlignment();
          break;
        case ACTION_ECHO_SCAN:
          HEA.beginEchoScan();
          action_end_time = millis() + 5000;
          break;
        case ACTION_ALIGN_ROBOT:
          action_end_time = millis() + 5000;
          robot_destination_angle = action_angle;
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

  // STEP 1: Performing the action until the termination conditions are triggered
  // When termination conditions are triggered, stop the action and proceed to step 2
  if (interaction_step == 1)
  {
    switch (action)
    {
      case ACTION_GO_ADVANCE:
        if (shock_event > 0 && !FCR._is_enacting){
          // If shock then stop the go advance action
          status ="SHOCK EVENT 1";
          action_end_time = 0;
          OWM.stopMotion();
          interaction_step = 2;
          break;
        }
      case ACTION_SHIFT_RIGHT:
      case ACTION_SHIFT_LEFT:
      case ACTION_TURN_RIGHT:
      case ACTION_TURN_LEFT:
        // Check if Floor Change Retreat
        if (FCR._is_enacting) {
          FCR.extraDuration(RETREAT_EXTRA_DURATION); // Increase retreat duration because need to reverse speed
          status ="1";
          //if (FCR._floor_outcome > 0) {
          //  status ="2";  // Check whether floor outcome has been set at this point
          //}
          // Proceed to step 2 for enacting Floor Change Retreat
          action_end_time = 0;
          interaction_step = 2;
        }
        // If no floor change, check whether duration has elapsed
        else if (action_end_time < millis()) {
          OWM.stopMotion();
          interaction_step = 2;
        }
        break;
      case ACTION_TURN_IN_SPOT_LEFT:
        // Keep head aligned with destination angle
        HEA.turnHead(robot_destination_angle - IMU._yaw);
         // Stop before reaching 45° or when duration has elapsed
        if ((IMU._yaw > robot_destination_angle - TURN_SPOT_ENDING_ANGLE) || (action_end_time < millis()))
        {
          OWM.stopMotion();
          interaction_step = 2;
          action_end_time = millis() + TURN_SPOT_ENDING_DELAY; // Add time for stabilisation during step 2
        }
        break;
      case ACTION_TURN_IN_SPOT_RIGHT:
        // Keep head aligned with destination angle
        HEA.turnHead(robot_destination_angle - IMU._yaw);
         // Stop before reaching -45° or when duration has elapsed
        if ((IMU._yaw < robot_destination_angle + TURN_SPOT_ENDING_ANGLE) || (action_end_time < millis()))
        {
          OWM.stopMotion();
          interaction_step = 2;
          action_end_time = millis() + TURN_SPOT_ENDING_DELAY; // Add time for stabilisation during step 2
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
      case ACTION_SCAN_DIRECTION:
        if (!HEA._is_enacting_head_alignment && !HEA._is_enacting_echo_scan)
        {
          action_end_time = 0;
          interaction_step = 2;
        }
        break;
      default:
        if (action_end_time < millis()) {
          OWM.stopMotion();
          interaction_step = 2;
        }
        break;
    }
  }

  // STEP 2: Enacting the termination of the interaction:
  // - Floor change retreat
  // - Stabilisation time
  // When the terminations are finished, proceed to Step 3
  if (interaction_step == 2)
  {
    // Wait for the interaction to terminate and proceed to Step 3
    // (Don't wait for  the head alignment or it may never terminate)
    if (action_end_time < millis() &&  !FCR._is_enacting && !HEA._is_enacting_head_alignment)
    {
      interaction_step = 3;
    }
  }

  // STEP 3: Ending of interaction:
  // Send the outcome and go back to Step 0
  if ((interaction_step == 3))
  {
    // Compute the outcome message
    JSONVar outcome_object;
    outcome_object["status"] = status;
    FCR.outcome(outcome_object);
    HEA.outcome(outcome_object);
    IMU.outcome(outcome_object);
    outcome_object["duration"] = millis() - action_start_time;
    String outcome_json_string = JSON.stringify(outcome_object);

    // Serial.println("Outcome string " + outcome_json_string);

    digitalWrite(LED_BUILTIN, HIGH); // light the led during transfer
    // Send the outcome to the IP address and port that sent the action
    Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    Udp.print(outcome_json_string);
    Udp.endPacket();
    digitalWrite(LED_BUILTIN, LOW);

    // Ready to begin a new interaction
    interaction_step = 0;
  }
}
