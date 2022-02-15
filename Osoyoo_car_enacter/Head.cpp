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
#include "Head.h"
#include <Arduino.h>
#include "Head_Dist.h"

Head::Head(){
  }

void Head::servo_port() {
  head_servo.attach(4);
}

int Head::getIndexMin(int nb_mesures, float distances[]){  
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

int Head::scan(int angleMin, int angleMax, int Nbre_mesure, int index_0) {
  int pas = round((angleMax-angleMin)/Nbre_mesure);
  float distances[Nbre_mesure];
  int indexMin;
  int angle;
  for (int pos = 0; pos <= Nbre_mesure; pos++) {
    head_servo.write(angleMin+(pas*pos));
    delay(300);
    distances[pos] = distUS.dist();
  } 
  indexMin = getIndexMin(Nbre_mesure, distances);
  angle = (indexMin + index_0)*pas;
  head_servo.write(angle);
  return angle;
}

int Head::miniScan(int angle){
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

void Head::distances_loop(int angle, float mesure){
    float distance = distUS.dist();
    Serial.print("distance : ");
    Serial.println(distance);
    Serial.print("mesure : ");
    Serial.println(mesure);
    if(mesure != 0 && distance - mesure > 50){
        miniScan(angle);
        Serial.println("distance - mesure : ");
        Serial.println(distance - mesure);
        Serial.println("Scan_1");
    }
}
