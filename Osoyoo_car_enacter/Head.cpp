#include <Servo.h>
#include "Head.h"
#include <Arduino.h>
#include "calcDist.h"

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
    distances[pos] = dist();
  } 
  indexMin = getIndexMin(Nbre_mesure, distances);
  angle = (indexMin + index_0)*pas;
  head_servo.write(angle);
  return angle;
}
