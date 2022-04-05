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
/**Connection à l'ambranchement du port du capteur rotatif servo**/
void Head::servo_port() {
  head_servo.attach(4);
}

/**
Deduit la valeur de l'index contenant la plus petite distance dans le tableau de distance des mersures de scan
@nb_mesures : Nombre de mesure effectuer au cours du scan
@distances[] : enregistre un tableau de taille @nb_mesures-1 qui enregistre à chaque intervalle une mesure lors du scan
**/
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

/**
    Scan entre 0 et 180 degré devant la tete du robot afin de s'aligner à l'objet la plus proche
    @angleMin : angle minimum du debut de scan
    @angleMax : angle maximum pour la fin de scan
    @Nbre_mesure : Nombre de mesure à effectuer permettant de determiner l'angle de saut de scan
    @index_0 : sert à determiner l'angle de debut du @miniScan dependant de l'alignement du scan
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
    Effectue un miniScan si la @mesure de l'alignement enregistrer differe de la @distance actuelle en integrant une marge de 50cm
    @angle : angle de l'alignement de la tete apres le scan
    La fonction n'est pas appelé dans le projet car bug du capteur ultra son
**/
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
    Fonction qui permet de mesurer à intervalle regulier une distance par rapport à un objet
    @param1 : angle retourner de l'alignement du scan
    @param2 : variable de mesure de distance memoriser lors du dernier alignement
**/
void Head::distances_loop(int angle, float mesure){
    float distance = distUS.dist();
    if(mesure != 0 && distance - mesure > 50){
        miniScan(angle);
    }
}
