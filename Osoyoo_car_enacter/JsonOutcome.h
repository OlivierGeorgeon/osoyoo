#ifndef JsonOutcome_h
#define JsonOutcome_h

#include "Arduino_JSON.h"

class JsonOutcome
{
  public:
    //Constructeur
    JsonOutcome();

    //Variable qui contient toute les données json
    JSONVar data;

    //Méthode pour ajouter une key/value à data
    void addValue(char key[], char value[]);

    //Méthode pour récuperer les données à envoyer par le wifi
    String get();
};

#endif