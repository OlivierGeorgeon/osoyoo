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
  myservo.attach(13);
}

void scan() {
  float distances[10];
  //Scan de 9 calcul de distances tout les 20 degrés pour couvrir les 180°
  for (int pos = 0; pos <= 9; pos += 1) {
    myservo.write(pos*20);
    delay(300);
    distances[pos] = dist();
  }

  //Recherche de la plus petite distances
  int indexMin;
  float valMin = distances[0];
  for (int i = 1; i <= 9; i++){
    if(distances[i] < varMin){
        valMin = distances[i];
        indexMin = i;
    }
  }
   myservo.write(indexMin*20); //S'aligner sur l'objet la plus proche
}
