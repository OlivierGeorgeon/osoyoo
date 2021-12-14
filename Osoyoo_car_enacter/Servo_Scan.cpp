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
  
  //Recherche de la plus petite distances
  for (int i = 0; i < nb_mesures; i++){
    if(distances[i] < valMin && distances[i] != 0){
        valMin = distances[i];
        indexMin = i;
    }
  }
  return indexMin;
}

int scan(int angleMin, int angleMax, int Nbre_mesure) {
  int pas = round((angleMax-angleMin)/Nbre_mesure);
  float distances[Nbre_mesure];
  int indexMin;
  int angle;
  //Scan de Nbre_mesure calcul de distances tout les 20 degrés pour couvrir les 180°
  for (int pos = 0; pos < Nbre_mesure; pos++) {
    myservo.write(angleMin+(pas*pos));
    delay(300);
    distances[pos] = dist();
    
  }
  

  
  // Appel fonction
  indexMin = getIndexMin(Nbre_mesure, distances);
  angle = indexMin*pas;
  myservo.write(angle);
  return angle;
}
