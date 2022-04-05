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
/**Connection to the servo rotary sensor port**/
void Head::servo_port() {
  head_servo.attach(4);
}

/**
Deducts the value of the index containing the smallest distance in the distance table of the scan measures
@nb_mesures : Number of measurements made during the scan
@distances[] : saves an array of size @nb_measurements-1 which records at each interval a measurement during the scan
**/
int Head::getIndexMin(int nb_mesures, float distances[]){
  float valMin = distances[0];
  int indexMin = 0;
  //Search for the smallest distance of the scan function for alignment
  for (int i = 0; i < nb_mesures; i++){
    if(distances[i] < valMin && distances[i] != 0){
        valMin = distances[i];
        indexMin = i;
    }
  }
  return indexMin;
}

/**
    Scan between 0 and 180 degrees in front of the robot head to align with the closest object
    @angleMin : minimum scan start angle
    @angleMax : maximum angle for the end of the scan
    @Nbre_mesure : Number of measurements to determine the scan jump angle
    @index_0 : is used to determine the starting angle of the @miniScan depending on the scan alignment
**/
void Head::scan(int angleMin, int angleMax, int Nbre_mesure, int index_0) {
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
  current_angle = angle;
}


/**
    Performs a miniScan if the recorded @alignment measurement differs from the current @distance with a 50mm margin
    @angle : head alignment angle after the scan
    he function is not called in the project because bug of the ultra sound sensor**/
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


/**
    Function that allows to measure at regular intervals a distance from an object
    @param1 : angle from the scan alignment
    @param2 : distance measurement variable stored during the last alignment
**/
void Head::distances_loop(int angle, float mesure){
    float distance = distUS.dist();
    if(mesure != 0 && distance - mesure > 50){
        miniScan(angle);
    }
    else if (mesure != 0 && distance - mesure < 50){
        miniScan(angle);
    }
}
