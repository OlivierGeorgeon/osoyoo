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

Servo myservo;
// Initialisation de port de branchement sur la carte
void servo_port() {
  myservo.attach(4);
}
void scan(int angleMin, int angleMax, int Nbre_mesure) {
  float pas = (angleMax-angleMin)/Nbre_mesure;
  float distances[Nbre_mesure];
  //Scan de Nbre_mesure calcul de distances tout les 20 degrés pour couvrir les 180°
  for (int pos = 0; pos <= Nbre_mesure; pos += 1) {
    myservo.write(angleMin+(pas*pos));
    delay(300);
    distances[pos] = dist();
  }
  //Recherche de la plus petite distances
  int indexMin;
  float valMin = distances[0];
  for (int i = 1; i <= Nbre_mesure; i++){
    if(distances[i] < valMin){
        valMin = distances[i];
        indexMin = i;
        Serial.print(indexMin, pas);
    }
  }
   myservo.write(indexMin*pas);
}
