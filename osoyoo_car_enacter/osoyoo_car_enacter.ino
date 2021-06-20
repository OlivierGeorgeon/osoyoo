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
#include <Servo.h>
#include <WiFiEsp.h>
#include <WiFiEspUDP.h>

#define SPEED 85    
#define TURN_SPEED 90  
#define SHIFT_SPEED 130  

#define TURN_TIME 500  
#define MOVE_TIME 500  

#define speedPinR 9   //  RIGHT WHEEL PWM pin D45 connect front MODEL-X ENA 
#define RightMotorDirPin1  22    //Front Right Motor direction pin 1 to Front MODEL-X IN1  (K1)
#define RightMotorDirPin2  24   //Front Right Motor direction pin 2 to Front MODEL-X IN2   (K1)                                 
#define LeftMotorDirPin1  26    //Left front Motor direction pin 1 to Front MODEL-X IN3 (  K3)
#define LeftMotorDirPin2  28   //Left front Motor direction pin 2 to Front MODEL-X IN4 (  K3)
#define speedPinL 10   // Left WHEEL PWM pin D7 connect front MODEL-X ENB

#define speedPinRB 11   //  RIGHT WHEEL PWM pin connect Back MODEL-X ENA 
#define RightMotorDirPin1B  5    //Rear Right Motor direction pin 1 to Back MODEL-X IN1 (  K1)
#define RightMotorDirPin2B 6    //Rear Right Motor direction pin 2 to Back MODEL-X IN2 (  K1) 
#define LeftMotorDirPin1B 7    //Rear left Motor direction pin 1 to Back MODEL-X IN3  K3
#define LeftMotorDirPin2B 8  //Rear left Motor direction pin 2 to Back MODEL-X IN4  k3
#define speedPinLB 12    //   LEFT WHEEL  PWM pin D8 connect Rear MODEL-X ENB

#define sensor1   A4 // Left most sensor
#define sensor2   A3 // 2nd Left   sensor
#define sensor3   A2 // center sensor
#define sensor4   A1 // 2nd right sensor
#define sensor5   A0 // Right most sensor

#define SERVO_PIN     13  //servo connect to D5
#define Echo_PIN    31 // Ultrasonic Echo pin connect to A5
#define Trig_PIN    30  // Ultrasonic Trig pin connect to A4
Servo head;
Floor_change_retreat FCR;

/*motor control*/
void right_shift(int speed_fl_fwd,int speed_rl_bck ,int speed_rr_fwd,int speed_fr_bck) {
  FL_fwd(speed_fl_fwd); 
  RL_bck(speed_rl_bck); 
  FR_bck(speed_fr_bck);
  RR_fwd(speed_rr_fwd);
}

void set_motion(int speed_fl, int speed_rl, int speed_rr, int speed_fr){
  front_left_wheel(speed_fl);
  rear_left_wheel(speed_rl);
  front_right_wheel(speed_fr);
  rear_right_wheel(speed_rr);
}

void left_shift(int speed_fl_bck,int speed_rl_fwd ,int speed_rr_bck,int speed_fr_fwd){
   FL_bck(speed_fl_bck);
   RL_fwd(speed_rl_fwd);
   FR_fwd(speed_fr_fwd);
   RR_bck(speed_rr_bck);
  
}
void go_advance(int speed){
   RL_fwd(speed);
   RR_fwd(speed);
   FR_fwd(speed);
   FL_fwd(speed); 
}
void  go_back(int speed){
   RL_bck(speed);
   RR_bck(speed);
   FR_bck(speed);
   FL_bck(speed); 
}
void left_turn(int speed){
   RL_bck(0);
   RR_fwd(speed);
   FR_fwd(speed);
   FL_bck(0); 
}
void right_turn(int speed){
   RL_fwd(speed);
   RR_bck(0);
   FR_bck(0);
   FL_fwd(speed); 
}
void left_back(int speed){
   RL_fwd(0);
   RR_bck(speed);
   FR_bck(speed);
   FL_fwd(0); 
}
void right_back(int speed){
   RL_bck(speed);
   RR_fwd(0);
   FR_fwd(0);
   FL_bck(speed); 
}

void clockwise(int speed){
   RL_fwd(speed);
   RR_bck(speed);
   FR_bck(speed);
   FL_fwd(speed); 
}
void count_clockwise(int speed){
   RL_bck(speed);
   RR_fwd(speed);
   FR_fwd(speed);
   FL_bck(speed); 
}

void right_shift(int speed){
  RL_bck(speed); 
  RR_fwd(speed);
  FR_bck(speed);
  FL_fwd(speed); 
}
void left_shift(int speed){
   RL_fwd(speed);
   RR_bck(speed);
   FR_fwd(speed);
   FL_bck(speed);
}
/*motor control*/
void front_right_wheel(int speed)
{
  if (speed > 0) {
    // Forward
    digitalWrite(RightMotorDirPin1,LOW);
    digitalWrite(RightMotorDirPin2,HIGH);
    analogWrite(speedPinR,speed);
  } else {
    // Backward
    digitalWrite(RightMotorDirPin1,HIGH);
    digitalWrite(RightMotorDirPin2,LOW);
    analogWrite(speedPinR,-speed);
  }
}
void front_left_wheel(int speed)
{
  if (speed > 0) {
    // Forward
    digitalWrite(LeftMotorDirPin1,LOW);
    digitalWrite(LeftMotorDirPin2,HIGH);
    analogWrite(speedPinL,speed);
  } else {
    // Backward
    digitalWrite(LeftMotorDirPin1,HIGH);
    digitalWrite(LeftMotorDirPin2,LOW);
    analogWrite(speedPinL,-speed);
  }
}
void rear_right_wheel(int speed)
{
  if (speed > 0) {
    // Forward
    digitalWrite(RightMotorDirPin1B, LOW);
    digitalWrite(RightMotorDirPin2B,HIGH);
    analogWrite(speedPinRB,speed);
  } else {
    // Backward
    digitalWrite(RightMotorDirPin1B, HIGH);
    digitalWrite(RightMotorDirPin2B,LOW);
    analogWrite(speedPinRB,-speed);
  }
}
void rear_left_wheel(int speed)
{
  if (speed > 0) {
    // Forward
    digitalWrite(LeftMotorDirPin1B,LOW);
    digitalWrite(LeftMotorDirPin2B,HIGH);
    analogWrite(speedPinLB,speed * 1.2); // Extra voltage because this wheel is weak
  } else {
    // Backward
    digitalWrite(LeftMotorDirPin1B,HIGH);
    digitalWrite(LeftMotorDirPin2B,LOW);
    analogWrite(speedPinLB,-speed * 1.2); // Extra voltage because this wheel is weak
  }
}


void FR_bck(int speed)  //front-right wheel backward turn
{
  digitalWrite(RightMotorDirPin1,HIGH);
  digitalWrite(RightMotorDirPin2,LOW); 
  analogWrite(speedPinR,speed);
}
void FR_fwd(int speed) // front-right wheel forward turn
{
  digitalWrite(RightMotorDirPin1,LOW);
  digitalWrite(RightMotorDirPin2,HIGH); 
  analogWrite(speedPinR,speed);
}
void FL_bck(int speed) // front-left wheel backward turn
{
  digitalWrite(LeftMotorDirPin1,HIGH);
  digitalWrite(LeftMotorDirPin2,LOW);
  analogWrite(speedPinL,speed);
}
void FL_fwd(int speed) // front-left wheel forward turn
{
  digitalWrite(LeftMotorDirPin1,LOW);
  digitalWrite(LeftMotorDirPin2,HIGH);
  analogWrite(speedPinL,speed);
}

void RR_bck(int speed)  //rear-right wheel backward turn
{
  digitalWrite(RightMotorDirPin1B, HIGH);
  digitalWrite(RightMotorDirPin2B,LOW); 
  analogWrite(speedPinRB,speed);
}
void RR_fwd(int speed)  //rear-right wheel forward turn
{
  digitalWrite(RightMotorDirPin1B, LOW);
  digitalWrite(RightMotorDirPin2B,HIGH); 
  analogWrite(speedPinRB,speed);
}
void RL_bck(int speed)  //rear-left wheel backward turn
{
  digitalWrite(LeftMotorDirPin1B,HIGH);
  digitalWrite(LeftMotorDirPin2B,LOW);
  analogWrite(speedPinLB,speed * 1.2); // Extra voltage because this wheel is weak
}
void RL_fwd(int speed)    //rear-left wheel forward turn
{
  digitalWrite(LeftMotorDirPin1B,LOW);
  digitalWrite(LeftMotorDirPin2B,HIGH);
  analogWrite(speedPinLB,speed * 1.2); // Extra voltage because this wheel is weak
}
 
void stop_motion()    //Stop
{
  analogWrite(speedPinLB,0);
  analogWrite(speedPinRB,0);
  analogWrite(speedPinL,0);
  analogWrite(speedPinR,0);
}


//Pins initialize
void init_GPIO()
{
  pinMode(RightMotorDirPin1, OUTPUT); 
  pinMode(RightMotorDirPin2, OUTPUT); 
  pinMode(speedPinL, OUTPUT);
 
  pinMode(LeftMotorDirPin1, OUTPUT);
  pinMode(LeftMotorDirPin2, OUTPUT); 
  pinMode(speedPinR, OUTPUT);
  pinMode(RightMotorDirPin1B, OUTPUT); 
  pinMode(RightMotorDirPin2B, OUTPUT); 
  pinMode(speedPinLB, OUTPUT);  
 
  pinMode(LeftMotorDirPin1B, OUTPUT);
  pinMode(LeftMotorDirPin2B, OUTPUT); 
  pinMode(speedPinRB, OUTPUT);
   
  stop_motion();

  // init HC-SR04 ultrasonic Echo sensor
  pinMode(Trig_PIN, OUTPUT); 
  pinMode(Echo_PIN,INPUT);
  digitalWrite(Trig_PIN,LOW);

  /*init servo*/
  head.attach(SERVO_PIN); 
  head.write(90);

  /*init floor sensors*/
  pinMode(sensor1, INPUT);
  pinMode(sensor2, INPUT);
  pinMode(sensor3, INPUT);
  pinMode(sensor4, INPUT);
  pinMode(sensor5, INPUT);
}

int status = WL_IDLE_STATUS;
// use a ring buffer to increase speed and reduce memory allocation
char packetBuffer[5];
WiFiEspUDP Udp;
unsigned int localPort = 8888;  // local port to listen on

void setup()
{
  init_GPIO();
  Serial.begin(9600);   // initialize serial for debugging
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

int previous_measure_floor = FCR.measureFloor();
unsigned long floor_change_retreat_end_time = 0;
bool is_enacting_floor_change_retreat = false;

unsigned long action_end_time = 0;
bool is_enacting_action = false;
char action =' ';

bool is_enacting_head_alignment = false;
unsigned long next_ultrasonic_measure_time = 0;
int penultimate_ultrasonic_measure = 1000;
int previous_ultrasonic_measure = 1000;
unsigned long next_saccade_time = 0;

//int previous_measure_echo = 1000;
//int penultimate_measure_echo = 1000;
int head_angle = 90; // from 20° (right) to 160° (left)
int head_angle_interval = 10;

String outcome = "0";

void loop()
{
  // Detect change in the floor measure
  int current_measure_floor = FCR.measureFloor();
  int floor_change = current_measure_floor ^ previous_measure_floor; // Bitwise XOR
  previous_measure_floor = current_measure_floor;


  if (is_enacting_floor_change_retreat)
  {
    if (millis() > floor_change_retreat_end_time) {
      // End floor change retreat
      stop_motion();
      Serial.println("End retreat at " + String(millis()));
      is_enacting_floor_change_retreat = false;
    }
  }
  else // If is not enacting floor change retreat
  {
    if (floor_change != 0)
    {
      // Begin floor change retreat
      Serial.println("Floor change " + String(floor_change, BIN) + " Begin retreat at " + String(millis()));
      is_enacting_floor_change_retreat = true;
      switch (floor_change) {
        case 0b10000:set_motion(-150,-150,-50,-50);break; // back right
        case 0b11000:set_motion(-150,-150,-50,-50);break; // back right
        case 0b00011:set_motion(-50,-50,-150,-150);break; // back left
        case 0b00001:set_motion(-50,-50,-150,-150);break; // back left
        default:go_back(150);break;
      }
      floor_change_retreat_end_time = millis() + 200;
      if (is_enacting_action) {
        floor_change_retreat_end_time += 100; // Give it more time to reverse direction
        outcome = "1";
        action_end_time = 0; // Terminate the action so it can send the outcome
      }
    }
  }

  if (is_enacting_head_alignment)
  {
    if (next_saccade_time < millis()) {
      next_saccade_time = millis() + 150; // servo specification speed is 120ms/60°
      int current_ultrasonic_measure = measure_ultrasonic_echo();
      Serial.println("Angle " +String(head_angle) + " measure " + String(current_ultrasonic_measure));
      if (previous_ultrasonic_measure > current_ultrasonic_measure ) {
        // Moving closer
        if ((head_angle > 10) && (head_angle < 170)) {
          head_angle += head_angle_interval;
          head.write(head_angle);
        } else {
          Serial.println("End head alignment at edge angle " + String(head_angle));
          is_enacting_head_alignment = false;
          action_end_time = 0;
        }
      } else {
        // moving away, reverse movement
        head_angle_interval = - head_angle_interval;
        head_angle += head_angle_interval;
        head.write(head_angle);
        if (penultimate_ultrasonic_measure >= previous_ultrasonic_measure) {
          // Passed the minimum, stop
          Serial.println("End head alignment at angle " + String(head_angle));
          is_enacting_head_alignment = false;
          action_end_time = 0;
        }
      }
      penultimate_ultrasonic_measure = previous_ultrasonic_measure;
      previous_ultrasonic_measure = current_ultrasonic_measure;
    }
  }
  /*else // If not enacting head alignment
  {
    // Trigger head alignment
    if (next_ultrasonic_measure_time < millis()) {
      next_ultrasonic_measure_time = millis() + 100;
      int current_ultrasonic_measure = measure_ultrasonic_echo();
      int ultrasonic_measure_change = current_ultrasonic_measure - previous_ultrasonic_measure;
      penultimate_ultrasonic_measure = previous_ultrasonic_measure;
      previous_ultrasonic_measure = current_ultrasonic_measure;
      if ((ultrasonic_measure_change < -50) && (previous_ultrasonic_measure < 400)) {
        is_enacting_head_alignment = true;
        Serial.print("Ultrasonic measure change ");
        Serial.println(ultrasonic_measure_change);
      }
    }
  }*/

  if (is_enacting_action)
  {
    if (action_end_time < millis())
    {
      //char outcome = '0';
      switch (action)
      {
        case 'A':
          if (!is_enacting_floor_change_retreat) {
          //  outcome = '1';
          //} else {
            stop_motion(); // Stop motion unless a reflex is being enacted
          }
          break;
        case 'C':
          if (is_enacting_head_alignment) {
            outcome = "1";
          } else {
            stop_motion();
          }
          break;
        case 'E':
          outcome = String(measure_ultrasonic_echo()) ;
          //outcome = outcome + String(previous_measure_echo, outcome);
          break;
      }
      is_enacting_action = false;
      // Send the outcome to the IP address and port that sent the action
      Serial.println("Outcome string " + outcome);
      // char outcome_char[outcome.length()+1]; // One more char for the null end of string
      // outcome.toCharArray(outcome_char, outcome.length()+1);
      // Serial.println("Sending outcome " + String(outcome_char));
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.print(outcome);
      //Udp.write(outcome_char);
      Udp.endPacket();
    }
    else // If action being enacted
    {
      if (action == 'C') {
        if (is_enacting_head_alignment) {
          stop_motion();
          action_end_time = 0;
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
      outcome = "0";
      switch (action)    //serial control instructions
      {
        case 'A':go_advance(SPEED);break;
        case 'L':left_turn(TURN_SPEED);break;
        case 'R':right_turn(TURN_SPEED);break;
        case 'B':go_back(SPEED);break;
        case 'S':stop_motion();break;
        case 'F':left_shift(0,150,0,150);break; //left ahead
        case 'H':right_shift(180,0,150,0);break; //right ahead
        case 'I':left_shift(150,0,150,0);break;//left back
        case 'K':right_shift(0,130,0,130);break;//right back
        case 'O':left_shift(200,150,150,200);break;//left shift
        case 'T':right_shift(200,200,200,200);break;//left shift
        case 'C': //turn in spot clockwise
          head_angle = 60; // Look ahead
          head.write(head_angle);
          clockwise(TURN_SPEED);
          break;
        case 'G':count_clockwise(TURN_SPEED);break;//turn in spot counterclockwise
        case '4':left_shift(SPEED);break;
        case '6':right_shift(SPEED);break;
        case 'E': // Align head
          is_enacting_head_alignment = true;
          action_end_time = millis() + 10000;
          penultimate_ultrasonic_measure = 0;
          previous_ultrasonic_measure = 1;
          break;
        default:break;
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

/*detection of ultrasonic distance*/
int measure_ultrasonic_echo()
{
  long echo_distance;
  digitalWrite(Trig_PIN,LOW);
  delayMicroseconds(5);                                                                              
  digitalWrite(Trig_PIN,HIGH);
  delayMicroseconds(15);
  digitalWrite(Trig_PIN,LOW);
  echo_distance=pulseIn(Echo_PIN,HIGH);
  echo_distance=echo_distance*0.1657; //how far away is the object in mm
  //Serial.print("Echo measure (mm): ");
  //Serial.println((int)echo_distance);
  return round(echo_distance);
}

/*int measure_floor()
{
  int s0 = !digitalRead(sensor1); // Left sensor
  int s1 = !digitalRead(sensor2);
  int s2 = !digitalRead(sensor3);
  int s3 = !digitalRead(sensor4);
  int s4 = !digitalRead(sensor5); // Right sensor
  int sensor_value=32;
  // from left to right: 1 when floor is dark and sensor's led is on
  sensor_value +=s0*16+s1*8+s2*4+s3*2+s4;
  //Serial.print("Flor sensor: ");
  //Serial.println(String(sensor_value, BIN));
  return sensor_value;
}
*/