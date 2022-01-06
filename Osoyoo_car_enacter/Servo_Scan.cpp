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
int getIndexMin(int nb_mesures, float distances[]){
  
  float valMin = distances[0];
  int indexMin = 0;
  
  //Recherche de la plus petite distances de la fonction de scan pour alignement
  for (int i = 0; i < nb_mesures; i++){
    if(distances[i] < valMin && distances[i] != 0){
        valMin = distances[i];
        indexMin = i;
    }
  }
  return indexMin;
}

//Fonction de full scan ballayant une zone de 180° devant le robot et assure l'alignement à l'objet la plus proche
int scan(int angleMin, int angleMax, int Nbre_mesure, int index_0) {
  int pas = round((angleMax-angleMin)/Nbre_mesure);
  float distances[Nbre_mesure];
  int indexMin;
  int angle;
  for (int pos = 0; pos < Nbre_mesure; pos++) {
    myservo.write(angleMin+(pas*pos));
    delay(300);
    distances[pos] = dist();  
  } 
  indexMin = getIndexMin(Nbre_mesure, distances);
  angle = (indexMin + index_0)*pas;
  Serial.println(dist());
  myservo.write(angle);
  return angle;
}

//Fonction permettant le suivi d'un objet detecté à l'aide des minis scan en 3 zones d'action
int MiniScan(int angle){
  if(angle > 0 && angle <= 60){
    scan(0, 60, 6, 0);
  }
  else if(angle > 60 && angle <=120){
    scan(60, 120, 6, 6);
  }
  else {
    scan(120, 180, 6, 12);
  }
}

void distances_loop(int angle, float mesure){
    Serial.print("Angle : ");
    Serial.println(angle);
    Serial.print("Mesure : ");
    Serial.println(mesure);
    Serial.print("Distance : ");
    float distance = dist();
    Serial.println(distance);
    if(mesure != 0 && distance - mesure > 50){
        MiniScan(angle);
        Serial.print(distance - mesure);
        Serial.print("Scan 1");
    }
}
