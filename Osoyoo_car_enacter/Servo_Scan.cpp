/*
 *  _____     _____     __      __   __     __   _______   __               _______         __         ___        ____   ______     __       ___
 * |  __  \  |  __  \  |  |    |  | |  \   |  | |   ____| |  |            /   _____|      /    \      |   \      /    | |   __  \  |  |    /     \
 * | |__|  | | |__|  | |  |    |  | |   \  |  | |  |__    |  |           /   /           /  /\  \     |    \    /     | |  |__|  | |  |   /   _   \
 * |     _/  |     _/  |  |    |  | |    \ |  | |     |   |  |          |   |  ____     /  /__\  \    |  |\  \ /  /|  | |  _____/  |  |  |   |  |  |
 * |  __  \  |  __  \  |  |    |  | |  |\ \|  | |   __|   |  |          |   |  |__ |   /   ____   \   |  |  \___/  |  | |  |       |  |  |   |_ |  |
 * | |__|  | | |  \  \ |   \__/   | |  | \    | |  |____  |  |____       \  \ _ |  |  /   /    \   \  |  |         |  | |  |       |  |   \       / 
 * |______/  |_|   \__\ \________/  |__|  \___| |_______| |_______|       \ _______| /__ /      \   \ |__|         |__| |__|       |__|    \ ___ /
 */


#include <Servo.h>
#include "calcDist.h"

#include "Servo_Scan.h"
#include "Arduino.h"

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position
double distances[10];

void servo_port() {
  myservo.attach(13);  // attaches the servo on pin 9 to the servo object
}

void scan() {
  myservo.write(90);
  for (pos = 0; pos <= 9; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos*20);              // tell servo to go to position in variable 'pos'
    delay(1000); 
    distances[pos] = dist();
    Serial.print(distances[pos]);
    Serial.print(" ; ");
    delay(1000);
  }
  for (pos = 0; pos <= 9; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos*20);              // tell servo to go to position in variable 'pos'
    delay(1000); 
    distances[pos] = dist();
    Serial.print(distances[pos]);
    Serial.print(" ; ");
    delay(1000);
  }
   myservo.write(90); //Remettre la tete en place
}
