#ifndef JsonOutcome_h
#define JsonOutcome_h

#include "Arduino_JSON.h"

class JsonOutcome
{
  public:
    /*
     * Constructor
     * Init before Robot setup function
     */
    JsonOutcome();

    /*
     * JSON Variable that contains all the data added with the method "get" json
     */
    JSONVar data;

    /*
     * Method for adding key/value in "data"
     * Execute in robot setup or loop fonction for each value to be added in "data"
     *
     * Example : jsonOutcome.addValue("distance", (String) calcDistance());
     */
    void addValue(char key[], String value);

    /*
     * Method for deleting all key/value of "data"
     * Execute after sending json data by wifi for clear data
     */
    void clear();

    /*
     * Method for get json data converted to string
     */
    String get();
};

#endif